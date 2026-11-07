from __future__ import annotations

import httpx

from app.research.adapters.base import SignalAdapter, SignalRecord
from app.utils.logging import get_logger

log = get_logger("adapter.papers")
PAPERS = "https://huggingface.co/api/daily_papers"


class PapersAdapter(SignalAdapter):
    name = "papers"
    default_limit = 6

    def fetch(self, limit: int | None = None) -> list[SignalRecord]:
        cap = limit or self.default_limit
        out: list[SignalRecord] = []
        try:
            with httpx.Client(timeout=15) as client:
                data = client.get(PAPERS).json()
            for item in (data or [])[:cap]:
                paper = item.get("paper") or item
                title = paper.get("title") or item.get("title") or "Untitled paper"
                paper_id = paper.get("id")
                out.append(
                    SignalRecord(
                        title=title,
                        category="research",
                        source="Hugging Face Daily Papers",
                        source_url=f"https://huggingface.co/papers/{paper_id}" if paper_id else "",
                        published_at=item.get("publishedAt") or paper.get("publishedAt") or "",
                        summary=(paper.get("summary") or item.get("summary") or "")[:500],
                        evidence=["hf-daily-papers"],
                        novelty_score=7.0,
                        momentum_score=6.0,
                        confidence=0.7,
                        tags=["research", "papers"],
                    )
                )
        except Exception as exc:
            log.warning(f"papers fetch failed: {exc}")
        return out
