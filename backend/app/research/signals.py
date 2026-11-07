from __future__ import annotations

from app.research.adapters import default_adapters
from app.utils.ids import new_id, utc_now
from app.utils.logging import get_logger

log = get_logger("signals")


def fetch_hackernews(limit: int = 8) -> list[dict]:
    from app.research.adapters.hackernews import HackerNewsAdapter

    return [_hydrate(r.to_dict()) for r in HackerNewsAdapter().fetch(limit=limit)]


def fetch_github(limit: int = 8) -> list[dict]:
    from app.research.adapters.github import GitHubAdapter

    return [_hydrate(r.to_dict()) for r in GitHubAdapter().fetch(limit=limit)]


def fetch_papers(limit: int = 6) -> list[dict]:
    from app.research.adapters.papers import PapersAdapter

    return [_hydrate(r.to_dict()) for r in PapersAdapter().fetch(limit=limit)]


def _hydrate(payload: dict) -> dict:
    payload = dict(payload)
    payload.setdefault("id", new_id("sig"))
    return payload


def collect_signals(*, max_queries: int = 24, live: bool = True) -> list[dict]:
    if not live:
        return []
    collected: list[dict] = []
    remaining = max_queries
    for adapter in default_adapters():
        if remaining <= 0:
            break
        batch = adapter.fetch(limit=min(adapter.default_limit, remaining))
        collected.extend(_hydrate(item.to_dict()) for item in batch)
        remaining -= 1
    ai_first = [
        sig
        for sig in collected
        if any(
            k in f"{sig.get('title','')} {sig.get('summary','')}".lower()
            for k in ("ai", "agent", "llm", "model", "mcp", "autonomous")
        )
    ]
    if ai_first:
        collected = ai_first + [s for s in collected if s not in ai_first]
    log.stage("signals collected", count=len(collected))
    for sig in collected:
        sig.setdefault("collected_at", utc_now().isoformat())
    return collected
