from __future__ import annotations

import json
import time
from typing import Any, Literal, TypeVar

import httpx
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.utils.logging import get_logger

log = get_logger("llm")
T = TypeVar("T", bound=BaseModel)
ModelTier = Literal["filter", "cheap", "reasoning", "strong", "coding", "default"]


class BudgetExceeded(RuntimeError):
    pass


class RunBudget:
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


class ModelRouter:
    """Provider-independent completion interface. Model names come from settings."""

    def __init__(self, budget: RunBudget | None = None) -> None:
        settings = get_settings()
        self.settings = settings
        self.provider = settings.llm_provider
        self.base_url = settings.llm_base_url.rstrip("/")
        self.temperature = settings.llm_temperature
        self.timeout = settings.llm_timeout_seconds
        self.openai_key = settings.openai_api_key
        self.anthropic_key = settings.anthropic_api_key
        self.gemini_key = settings.gemini_api_key
        self.budget = budget or RunBudget(
            settings.max_model_calls, settings.max_tokens, settings.max_runtime_minutes * 60
        )
        self._resolved_ollama_host: str | None = None
        self._using_ollama_fallback: bool = False

    def _probe_ollama(self, host: str) -> bool:
        native = host.rstrip("/")
        if not native:
            return False
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{native}/api/tags")
                response.raise_for_status()
            return True
        except Exception:
            return False

    def resolve_ollama_host(self) -> str | None:
        """Prefer OLLAMA_HOST; if /api/tags fails, use OLLAMA_FALLBACK_HOST (local)."""
        if self._resolved_ollama_host is not None:
            return self._resolved_ollama_host or None

        primary = (self.settings.ollama_host or "").rstrip("/")
        fallback = (self.settings.ollama_fallback_host or "").rstrip("/")

        if primary and self._probe_ollama(primary):
            self._resolved_ollama_host = primary
            self._using_ollama_fallback = False
            return primary

        if fallback and fallback != primary and self._probe_ollama(fallback):
            model = self.settings.ollama_fallback_model or "qwen3.5:latest"
            log.warning(
                f"ollama primary unreachable ({primary or 'unset'}); "
                f"falling back to {fallback} with model {model} for all tiers"
            )
            self._resolved_ollama_host = fallback
            self._using_ollama_fallback = True
            self.base_url = f"{fallback}/v1"
            return fallback

        self._resolved_ollama_host = ""
        self._using_ollama_fallback = False
        return None

    def available(self) -> bool:
        if self.provider == "ollama":
            return self.resolve_ollama_host() is not None
        if self.provider == "openai":
            return bool(self.openai_key)
        if self.provider == "anthropic":
            return bool(self.anthropic_key)
        if self.provider == "gemini":
            return bool(self.gemini_key)
        return False

    def probe(self) -> tuple[bool, str]:
        if self.provider == "ollama":
            host = self.resolve_ollama_host()
            if host:
                model = self._resolve_model("default")
                suffix = " (fallback)" if self._using_ollama_fallback else ""
                return True, f"ollama/{model} @ {host}{suffix}"
            return False, "ollama unavailable (primary and fallback)"
        if self.available():
            return True, f"{self.provider}/{self.settings.model_for_tier('default')}"
        return False, f"{self.provider} unavailable"

    def _resolve_model(self, tier: ModelTier) -> str:
        if self.provider == "ollama":
            self.resolve_ollama_host()
            if self._using_ollama_fallback:
                return self.settings.ollama_fallback_model or "qwen3.5:latest"
        return self.settings.model_for_tier(tier)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
    def complete(
        self,
        system: str,
        user: str,
        *,
        json_mode: bool = True,
        tier: ModelTier = "default",
        temperature: float | None = None,
    ) -> str:
        self.budget.check()
        model = self._resolve_model(tier)
        temp = temperature if temperature is not None else self.temperature
        self.budget.calls += 1
        log.stage(f"calling {self.provider}", model=model, tier=tier, call=self.budget.calls)
        started = time.monotonic()
        if self.provider == "openai":
            text = self._openai_complete(system, user, model=model, json_mode=json_mode, temperature=temp)
        elif self.provider == "anthropic":
            text = self._anthropic_complete(system, user, model=model, json_mode=json_mode, temperature=temp)
        elif self.provider == "gemini":
            text = self._gemini_complete(system, user, model=model, json_mode=json_mode, temperature=temp)
        else:
            text = self._ollama_complete(system, user, model=model, json_mode=json_mode, temperature=temp)
        elapsed = int((time.monotonic() - started) * 1000)
        approx_tokens = max(1, (len(system) + len(user) + len(text)) // 4)
        self.budget.tokens += approx_tokens
        log.stage(f"{self.provider} response", chars=len(text), ms=elapsed, tokens=approx_tokens)
        return text

    def complete_json(self, system: str, user: str, *, tier: ModelTier = "default") -> Any:
        last_error: Exception | None = None
        for attempt in range(self.settings.llm_max_retries + 1):
            try:
                return extract_json(self.complete(system, user, json_mode=True, tier=tier))
            except Exception as exc:
                last_error = exc
                log.warning(f"json parse retry {attempt + 1}: {exc}")
        raise last_error or ValueError("failed to parse json")

    def complete_model(self, system: str, user: str, model: type[T], *, tier: ModelTier = "default") -> T:
        payload = self.complete_json(system, user, tier=tier)
        if isinstance(payload, list) and hasattr(model, "model_fields") and "ideas" in model.model_fields:
            payload = {"ideas": payload}
        return model.model_validate(payload)

    def _ollama_complete(self, system: str, user: str, *, model: str, json_mode: bool, temperature: float) -> str:
        native = self.resolve_ollama_host()
        if not native:
            raise RuntimeError("Ollama unavailable (primary and fallback hosts failed /api/tags)")
        system_prompt = system
        if json_mode:
            system_prompt = f"{system}\n\nRespond with valid JSON only. No markdown. No thinking tags."
        payload: dict[str, Any] = {
            "model": model,
            "stream": False,
            "think": False,
            "options": {"temperature": temperature, "num_predict": 4096},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            payload["format"] = "json"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{native}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
        return (data.get("message") or {}).get("content") or ""

    def _openai_complete(self, system: str, user: str, *, model: str, json_mode: bool, temperature: float) -> str:
        if not self.openai_key:
            raise RuntimeError("OPENAI_API_KEY required for openai provider")
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        payload: dict[str, Any] = {
            "model": model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        url = self.settings.openai_base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]

    def _anthropic_complete(self, system: str, user: str, *, model: str, json_mode: bool, temperature: float) -> str:
        if not self.anthropic_key:
            raise RuntimeError("ANTHROPIC_API_KEY required for anthropic provider")
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 4096,
            "temperature": temperature,
            "system": system + ("\nRespond with JSON only." if json_mode else ""),
            "messages": [{"role": "user", "content": user}],
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        parts = data.get("content") or []
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text")

    def _gemini_complete(self, system: str, user: str, *, model: str, json_mode: bool, temperature: float) -> str:
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY required for gemini provider")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={self.gemini_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json" if json_mode else "text/plain",
            },
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return ""
        parts = (candidates[0].get("content") or {}).get("parts") or []
        return "".join(p.get("text", "") for p in parts)
