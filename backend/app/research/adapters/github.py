from __future__ import annotations

import random

import httpx

from app.config.settings import get_settings
from app.research.adapters.base import SignalAdapter, SignalRecord
from app.utils.logging import get_logger

log = get_logger("adapter.github")

GITHUB_SEARCH = "https://api.github.com/search/repositories"
QUERIES = [
    "agentic OR multi-agent OR \"autonomous agent\" pushed:>2025-01-01 stars:5..500",
    "\"agent identity\" OR \"agent authorization\" OR mcp pushed:>2025-01-01 stars:5..400",
    "\"computer use\" OR \"browser agent\" OR \"tool calling\" pushed:>2025-06-01 stars:10..500",
    "\"agent memory\" OR \"world model\" agent pushed:>2025-01-01 stars:5..300",
]


class GitHubAdapter(SignalAdapter):
    name = "github"
    default_limit = 8

    def _headers(self) -> dict[str, str]:
        settings = get_settings()
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "Nocta"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        return headers

    def fetch(self, limit: int | None = None) -> list[SignalRecord]:
        cap = limit or self.default_limit
        out: list[SignalRecord] = []
        q = random.choice(QUERIES)
        try:
            with httpx.Client(timeout=15) as client:
                data = client.get(
                    GITHUB_SEARCH,
                    params={"q": q, "sort": "updated", "order": "desc", "per_page": cap},
                    headers=self._headers(),
                ).json()
            for item in (data.get("items") or [])[:cap]:
                stars = item.get("stargazers_count") or 0
                out.append(
                    SignalRecord(
                        title=item.get("full_name") or item.get("name") or "repo",
                        category="developer",
                        source="GitHub",
                        source_url=item.get("html_url") or "",
                        published_at=item.get("pushed_at") or item.get("updated_at") or "",
                        summary=(item.get("description") or "Repository activity.")[:400],
                        evidence=[f"stars:{stars}"],
                        novelty_score=6.0 if stars < 200 else 4.5,
                        momentum_score=min(10.0, stars / 80),
                        confidence=0.75,
                        tags=(item.get("topics") or [])[:6],
                    )
                )
        except Exception as exc:
            log.warning(f"github fetch failed: {exc}")
        return out
