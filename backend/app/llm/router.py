from __future__ import annotations

import json
import time
from typing import Any, TypeVar
from urllib.parse import urlparse

import httpx
from openai import OpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.utils.logging import get_logger

log = get_logger("llm")
T = TypeVar("T", bound=BaseModel)

# Default task when callers omit one. FutureLab core work is HEAVY-bound via SharedRoute.
DEFAULT_TASK = "complex_reasoning"

# Known SharedRoute tasks (documentation aid). SharedRoute maps tasks to FAST / MEDIUM / HEAVY.
ROUTER_TASKS = frozenset(
    {
        # FAST
        "classification",
        "extraction",
        "metadata_extraction",
        "simple_summary",
        "short_rewrite",
        "formatting",
        "json_normalization",
        "validation",
        "simple_content",
        # MEDIUM
        "content_generation",
        "prompt_generation",
        "story_generation",
        "general_chat",
        "research_summary",
        "social_post",
        "document_summary",
        # HEAVY
        "complex_reasoning",
        "deep_analysis",
        "architecture",
        "code_generation",
        "code_review",
        "debugging",
        "deep_research",
        "repo_analysis",
        "agent_planning",
        "failure_recovery",
    }
)


class BudgetExceeded(RuntimeError):
    pass


class RunBudget:
    """Application-level call/token/runtime budget (not request max_tokens)."""

    def __init__(self, max_calls: int, max_tokens: int, max_runtime_seconds: float) -> None:
        self.max_calls = max_calls
        self.max_tokens = max_tokens
        self.max_runtime_seconds = max_runtime_seconds
        self.calls = 0
        self.tokens = 0
        self.started = time.monotonic()
        self.cost_usd = 0.0

    def remaining_seconds(self) -> float:
        return self.max_runtime_seconds - (time.monotonic() - self.started)

    def check(self) -> None:
        if self.calls >= self.max_calls:
            raise BudgetExceeded(f"model call budget exhausted ({self.max_calls})")
        if self.tokens >= self.max_tokens:
            raise BudgetExceeded(f"token budget exhausted ({self.max_tokens})")
        if self.remaining_seconds() <= 0:
            raise BudgetExceeded("runtime budget exhausted")


def extract_json(text: str) -> Any:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("empty LLM response")
    if raw.startswith("```"):
        lines = raw.splitlines()
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        raw = "\n".join(lines).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        start = raw.find("[")
        end = raw.rfind("]")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def shared_route_origin(base_url: str) -> str:
    """http://host:8088/v1 → http://host:8088"""
    parsed = urlparse(base_url.rstrip("/"))
    if not parsed.scheme or not parsed.netloc:
        return base_url.rstrip("/").removesuffix("/v1")
    return f"{parsed.scheme}://{parsed.netloc}"


class ModelRouter:
    """OpenAI-compatible client → SharedRoute only.

    Always uses ``model=AI_MODEL`` (default ``router``). Tier/backend selection is
    owned by SharedRoute via ``X-Route-Project`` + ``X-Route-Task`` headers.

    This application never contacts Ollama, oMLX node IPs, or physical model names.
    """

    def __init__(self, budget: RunBudget | None = None) -> None:
        settings = get_settings()
        self.settings = settings
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model = settings.ai_model
        self.project = settings.ai_project
        self.api_key = settings.openai_api_key or "unused"
        self.temperature = settings.llm_temperature
        self.timeout = settings.llm_timeout_seconds
        self.budget = budget or RunBudget(
            settings.max_model_calls, settings.max_tokens, settings.max_runtime_minutes * 60
        )
        self._client: OpenAI | None = None
        self._router_ok: bool | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout,
            )
        return self._client

    def _task_headers(self, task: str) -> dict[str, str]:
        return {
            "X-Route-Project": self.project,
            "X-Route-Task": task,
        }

    def _probe_router(self) -> bool:
        if self._router_ok is not None:
            return self._router_ok
        health_url = f"{shared_route_origin(self.base_url)}/health"
        try:
            with httpx.Client(timeout=5) as http:
                response = http.get(health_url)
                response.raise_for_status()
            self._router_ok = True
        except Exception as exc:
            log.warning(f"SharedRoute probe failed ({health_url}): {exc}")
            self._router_ok = False
        return self._router_ok

    def available(self) -> bool:
        return self._probe_router()

    def probe(self) -> tuple[bool, str]:
        if self._probe_router():
            return True, f"SharedRoute/{self.model} @ {self.base_url} project={self.project}"
        return False, f"SharedRoute unavailable ({self.base_url})"

    def call_llm(self, task: str, messages: list[dict[str, str]], *, temperature: float | None = None) -> Any:
        """Thin wrapper matching the shared-client pattern (no application max_tokens)."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature if temperature is None else temperature,
            extra_headers=self._task_headers(task),
        )

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
    def complete(
        self,
        system: str,
        user: str,
        *,
        json_mode: bool = True,
        task: str = DEFAULT_TASK,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        self.budget.check()
        temp = temperature if temperature is not None else self.temperature
        self.budget.calls += 1
        log.stage(
            "calling SharedRoute",
            model=self.model,
            task=task,
            project=self.project,
            call=self.budget.calls,
        )
        started = time.monotonic()
        text = self._router_complete(
            system,
            user,
            task=task,
            json_mode=json_mode,
            temperature=temp,
            max_tokens=max_tokens,
        )
        elapsed = int((time.monotonic() - started) * 1000)
        approx_tokens = max(1, (len(system) + len(user) + len(text)) // 4)
        self.budget.tokens += approx_tokens
        log.stage("SharedRoute response", chars=len(text), ms=elapsed, tokens=approx_tokens, task=task)
        return text

    def complete_json(self, system: str, user: str, *, task: str = DEFAULT_TASK) -> Any:
        last_error: Exception | None = None
        for attempt in range(self.settings.llm_max_retries + 1):
            try:
                return extract_json(self.complete(system, user, json_mode=True, task=task))
            except Exception as exc:
                last_error = exc
                log.warning(f"json parse retry {attempt + 1}: {exc}")
        raise last_error or ValueError("failed to parse json")

    def complete_model(self, system: str, user: str, model: type[T], *, task: str = DEFAULT_TASK) -> T:
        payload = self.complete_json(system, user, task=task)
        if isinstance(payload, list) and hasattr(model, "model_fields") and "ideas" in model.model_fields:
            payload = {"ideas": payload}
        return model.model_validate(payload)

    def _router_complete(
        self,
        system: str,
        user: str,
        *,
        task: str,
        json_mode: bool,
        temperature: float,
        max_tokens: int | None = None,
    ) -> str:
        system_prompt = system
        if json_mode:
            system_prompt = f"{system}\n\nRespond with valid JSON only. No markdown. No thinking tags."
        kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
            ],
            "extra_headers": self._task_headers(task),
        }
        # Only pass max_tokens when the caller explicitly needs a bounded output.
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**kwargs)
        return (response.choices[0].message.content or "") if response.choices else ""


# Backwards-compatible alias used by older imports / docs
router_origin = shared_route_origin
