from __future__ import annotations

import random
from datetime import datetime, timezone

import httpx

from app.config.settings import get_settings
from app.utils.ids import new_id, utc_now
from app.utils.logging import get_logger

log = get_logger("signals")

HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
GITHUB_SEARCH = "https://api.github.com/search/repositories"
PAPERS = "https://huggingface.co/api/daily_papers"


def _github_headers() -> dict[str, str]:
    settings = get_settings()
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "VectraFutureLab"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def fetch_hackernews(limit: int = 8) -> list[dict]:
    out: list[dict] = []
    try:
        with httpx.Client(timeout=12) as client:
            ids = client.get(HN_TOP).json()[:40]
            interesting = []
            for sid in ids:
                item = client.get(HN_ITEM.format(id=sid)).json() or {}
                title = (item.get("title") or "").lower()
                if any(k in title for k in ("ai", "agent", "llm", "model", "mcp", "autonomous", "orchestration")):
                    interesting.append(item)
            for item in interesting[:limit]:
                out.append(
                    {
                        "id": new_id("sig"),
                        "title": item.get("title") or "Untitled HN story",
                        "category": "developer",
                        "source": "Hacker News",
                        "source_url": item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}",
                        "published_at": datetime.fromtimestamp(item.get("time") or 0, tz=timezone.utc).isoformat(),
                        "summary": f"HN score {item.get('score', 0)}; {item.get('descendants', 0)} comments.",
                        "evidence": [f"hn:{item.get('id')}"],
                        "novelty_score": 5.5,
                        "momentum_score": min(10.0, (item.get("score") or 0) / 40),
                        "confidence": 0.8,
                        "tags": ["hackernews"],
                        "claim_type": "FACT",
                        "technologies": [],
                    }
                )
    except Exception as exc:
        log.warning(f"hackernews fetch failed: {exc}")
    return out


def fetch_github(limit: int = 8) -> list[dict]:
    queries = [
        "agentic OR multi-agent OR \"autonomous agent\" pushed:>2025-01-01 stars:5..500",
        "\"agent identity\" OR \"agent authorization\" OR mcp pushed:>2025-01-01 stars:5..400",
        "\"computer use\" OR \"browser agent\" OR \"tool calling\" pushed:>2025-06-01 stars:10..500",
        "\"agent memory\" OR \"world model\" agent pushed:>2025-01-01 stars:5..300",
    ]
    out: list[dict] = []
    q = random.choice(queries)
    try:
        with httpx.Client(timeout=15) as client:
            data = client.get(
                GITHUB_SEARCH,
                params={"q": q, "sort": "updated", "order": "desc", "per_page": limit},
                headers=_github_headers(),
            ).json()
        for item in (data.get("items") or [])[:limit]:
            out.append(
                {
                    "id": new_id("sig"),
                    "title": item.get("full_name") or item.get("name"),
                    "category": "developer",
                    "source": "GitHub",
                    "source_url": item.get("html_url") or "",
                    "published_at": item.get("pushed_at") or item.get("updated_at") or "",
                    "summary": (item.get("description") or "Repository activity.")[:400],
                    "evidence": [f"stars:{item.get('stargazers_count', 0)}"],
                    "novelty_score": 6.0 if (item.get("stargazers_count") or 0) < 200 else 4.5,
                    "momentum_score": min(10.0, (item.get("stargazers_count") or 0) / 80),
                    "confidence": 0.75,
                    "tags": (item.get("topics") or [])[:6],
                    "claim_type": "FACT",
                    "technologies": [],
                }
            )
    except Exception as exc:
        log.warning(f"github fetch failed: {exc}")
    return out


def fetch_papers(limit: int = 6) -> list[dict]:
    out: list[dict] = []
    try:
        with httpx.Client(timeout=15) as client:
            data = client.get(PAPERS).json()
        for item in (data or [])[:limit]:
            paper = item.get("paper") or item
            title = paper.get("title") or item.get("title") or "Untitled paper"
            out.append(
                {
                    "id": new_id("sig"),
                    "title": title,
                    "category": "research",
                    "source": "Hugging Face Daily Papers",
                    "source_url": paper.get("id") and f"https://huggingface.co/papers/{paper.get('id')}" or "",
                    "published_at": item.get("publishedAt") or paper.get("publishedAt") or "",
                    "summary": (paper.get("summary") or item.get("summary") or "")[:500],
                    "evidence": ["hf-daily-papers"],
                    "novelty_score": 7.0,
                    "momentum_score": 6.0,
                    "confidence": 0.7,
                    "tags": ["research", "papers"],
                    "claim_type": "FACT",
                    "technologies": [],
                }
            )
    except Exception as exc:
        log.warning(f"papers fetch failed: {exc}")
    return out


def collect_signals(*, max_queries: int = 24, live: bool = True) -> list[dict]:
    if not live:
        return []
    collected: list[dict] = []
    remaining = max_queries
    for fetcher, n in ((fetch_github, 8), (fetch_hackernews, 8), (fetch_papers, 6)):
        if remaining <= 0:
            break
        batch = fetcher(limit=min(n, remaining))
        collected.extend(batch)
        remaining -= 1
    # Soft preference: keep AI/agentic-looking signals first when mixed
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
