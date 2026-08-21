from __future__ import annotations

import re

# Hard scope: FutureLab only invents inside AI + Agentic AI.
AI_AGENTIC_KEYWORDS = (
    "ai",
    "a.i.",
    "artificial intelligence",
    "llm",
    "large language",
    "foundation model",
    "machine learning",
    "neural",
    "agent",
    "agentic",
    "multi-agent",
    "autonomous",
    "tool-calling",
    "tool calling",
    "computer use",
    "orchestration",
    "mcp",
    "rag",
    "embedding",
    "vector",
    "inference",
    "model router",
    "prompt",
    "copilot",
    "robotics",
)

# Require at least one agentic / systems signal so generic "AI notes" ideas still die elsewhere.
AGENTIC_KEYWORDS = (
    "agent",
    "agentic",
    "multi-agent",
    "autonomous",
    "tool-calling",
    "tool calling",
    "computer use",
    "orchestration",
    "workflow",
    "runtime",
    "capability",
    "authorization",
    "identity",
    "escrow",
    "memory",
    "world model",
    "mcp",
    "planner",
    "executor",
    "swarm",
)

DEFAULT_AI_THEME = "Autonomous AI Agents"


def _blob(*parts: str) -> str:
    return " ".join(p for p in parts if p).lower()


def _has_any(blob: str, keywords: tuple[str, ...]) -> bool:
    for kw in keywords:
        if " " in kw or "-" in kw or "." in kw:
            if kw in blob:
                return True
        elif re.search(rf"\b{re.escape(kw)}\b", blob):
            return True
    return False


def is_ai_agentic_scope(
    *,
    name: str = "",
    one_liner: str = "",
    problem: str = "",
    product: str = "",
    customer: str = "",
    theme: str = "",
    technology_convergence: list[str] | None = None,
) -> tuple[bool, str]:
    """Return (ok, reason). Reject anything outside AI / Agentic AI."""
    conv = " ".join(technology_convergence or [])
    blob = _blob(name, one_liner, problem, product, customer, theme, conv)

    if not blob.strip():
        return False, "Empty idea cannot be classified as AI/Agentic"

    has_ai = _has_any(blob, AI_AGENTIC_KEYWORDS)
    has_agentic = _has_any(blob, AGENTIC_KEYWORDS)

    if has_ai and has_agentic:
        return True, ""
    if has_ai and ("agent" in blob or "agentic" in blob or "autonomous" in blob):
        return True, ""
    if has_agentic and has_ai:
        return True, ""

    # Strong agentic product names (Agent Escrow, etc.) without repeating "AI"
    if has_agentic and any(tok in blob for tok in ("agent", "agentic", "mcp", "llm", "model")):
        return True, ""

    if not has_ai and not has_agentic:
        return False, "Out of scope: FutureLab only invents AI and Agentic AI products"
    if has_ai and not has_agentic:
        return False, "Out of scope: AI wrapper without an agentic/systems thesis"
    return False, "Out of scope: must be AI + Agentic AI"


def signal_is_ai_agentic(signal: dict) -> bool:
    blob = _blob(
        str(signal.get("title") or ""),
        str(signal.get("summary") or ""),
        " ".join(signal.get("tags") or []),
        " ".join(signal.get("technologies") or []),
    )
    return _has_any(blob, AI_AGENTIC_KEYWORDS) or _has_any(blob, AGENTIC_KEYWORDS)


def enforce_ai_theme(theme: str | None) -> str:
    raw = (theme or "").strip()
    if not raw:
        return DEFAULT_AI_THEME
    ok, _ = is_ai_agentic_scope(theme=raw, name=raw, one_liner=raw, product=raw)
    return raw if ok else DEFAULT_AI_THEME
