from __future__ import annotations

import re

from rapidfuzz import fuzz

_TOKEN_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = {
    "a",
    "an",
    "the",
    "for",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "with",
    "ai",
    "agent",
    "agents",
    "platform",
    "layer",
    "network",
    "system",
    "product",
}


def tokenize(text: str) -> set[str]:
    return {tok for tok in _TOKEN_RE.findall((text or "").lower()) if tok not in STOPWORDS and len(tok) > 2}


def idea_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    ratio = fuzz.token_set_ratio(left, right) / 100.0
    tokens_l, tokens_r = tokenize(left), tokenize(right)
    if not tokens_l or not tokens_r:
        return ratio
    jaccard = len(tokens_l & tokens_r) / max(1, len(tokens_l | tokens_r))
    return round(0.65 * ratio + 0.35 * jaccard, 4)
