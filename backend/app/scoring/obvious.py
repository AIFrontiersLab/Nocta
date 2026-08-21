from __future__ import annotations

import re

OBVIOUS_PATTERNS = [
    r"\bchatbot\b",
    r"\bmeeting summar",
    r"\bai writing assistant\b",
    r"\brag (saas|platform|app)\b",
    r"\bimage generator\b",
    r"\bgeneric crud\b",
    r"\bai[- ]powered notes\b",
    r"\bwrapper (for|around) (chatgpt|openai|claude)\b",
    r"\banother (ai )?(crm|notepad|todo)\b",
]

IMPOSSIBLE_PATTERNS = [
    r"\bfaster than light\b",
    r"\bteleport",
    r"\bagi that (replaces|runs) (all|every) compan",
    r"\bperfect prediction of (the )?future\b",
]


def is_obvious(text: str) -> tuple[bool, str]:
    blob = (text or "").lower()
    for pattern in OBVIOUS_PATTERNS:
        if re.search(pattern, blob):
            return True, f"Obvious pattern matched: {pattern}"
    commodity = ("just add ai" in blob) or ("chatgpt wrapper" in blob) or ("wrapper around gpt" in blob)
    if commodity:
        return True, "Commodity LLM wrapper language"
    return False, ""


def is_impossible(text: str) -> tuple[bool, str]:
    blob = (text or "").lower()
    for pattern in IMPOSSIBLE_PATTERNS:
        if re.search(pattern, blob):
            return True, f"Impossible pattern matched: {pattern}"
    return False, ""
