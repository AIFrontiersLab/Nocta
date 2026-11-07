from __future__ import annotations

import re


_WHITESPACE = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9\s\-_/]+")


def collapse_whitespace(text: str) -> str:
    return _WHITESPACE.sub(" ", (text or "").strip())


def slugify(text: str, *, max_len: int = 64) -> str:
    cleaned = _NON_ALNUM.sub("", collapse_whitespace(text).lower())
    slug = cleaned.replace(" ", "-").replace("_", "-")
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_len] or "item"


def clip(text: str, limit: int = 280) -> str:
    value = collapse_whitespace(text)
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + "…"


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    blob = (text or "").lower()
    return [k for k in keywords if k.lower() in blob]
