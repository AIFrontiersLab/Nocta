from datetime import datetime, timezone

from app.utils.text import clip, keyword_hits, slugify
from app.utils.timeboxes import night_window, within_last


def test_slugify_and_clip():
    assert slugify("Agent Escrow!!") == "agent-escrow"
    assert clip("hello world", 5).endswith("…")


def test_keyword_hits():
    assert keyword_hits("Autonomous AI agents", ["ai", "blockchain"]) == ["ai"]


def test_night_window_and_within_last():
    evening = datetime(2026, 11, 7, 23, 0, tzinfo=timezone.utc)
    afternoon = datetime(2026, 11, 7, 15, 0, tzinfo=timezone.utc)
    assert night_window(now=evening) is True
    assert night_window(now=afternoon) is False
    assert within_last(evening.isoformat(), hours=48) is True
