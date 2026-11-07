from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.research.adapters.base import SignalAdapter, SignalRecord
from app.utils.logging import get_logger

log = get_logger("adapter.hn")

HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
KEYWORDS = ("ai", "agent", "llm", "model", "mcp", "autonomous", "orchestration")


class HackerNewsAdapter(SignalAdapter):
    name = "hackernews"
    default_limit = 8

    def fetch(self, limit: int | None = None) -> list[SignalRecord]:
        cap = limit or self.default_limit
        out: list[SignalRecord] = []
        try:
            with httpx.Client(timeout=12) as client:
                ids = client.get(HN_TOP).json()[:40]
                interesting = []
                for sid in ids:
                    item = client.get(HN_ITEM.format(id=sid)).json() or {}
                    title = (item.get("title") or "").lower()
                    if any(k in title for k in KEYWORDS):
                        interesting.append(item)
                for item in interesting[:cap]:
                    out.append(
                        SignalRecord(
                            title=item.get("title") or "Untitled HN story",
                            category="developer",
                            source="Hacker News",
                            source_url=item.get("url")
                            or f"https://news.ycombinator.com/item?id={item.get('id')}",
                            published_at=datetime.fromtimestamp(
                                item.get("time") or 0, tz=timezone.utc
                            ).isoformat(),
                            summary=f"HN score {item.get('score', 0)}; {item.get('descendants', 0)} comments.",
                            evidence=[f"hn:{item.get('id')}"],
                            novelty_score=5.5,
                            momentum_score=min(10.0, (item.get("score") or 0) / 40),
                            confidence=0.8,
                            tags=["hackernews"],
                        )
                    )
        except Exception as exc:
            log.warning(f"hackernews fetch failed: {exc}")
        return out
