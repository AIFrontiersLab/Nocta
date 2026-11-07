from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SignalRecord:
    title: str
    category: str
    source: str
    source_url: str = ""
    published_at: str = ""
    summary: str = ""
    evidence: list[str] = field(default_factory=list)
    novelty_score: float = 5.0
    momentum_score: float = 5.0
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    claim_type: str = "FACT"
    technologies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "category": self.category,
            "source": self.source,
            "source_url": self.source_url,
            "published_at": self.published_at,
            "summary": self.summary,
            "evidence": list(self.evidence),
            "novelty_score": self.novelty_score,
            "momentum_score": self.momentum_score,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "claim_type": self.claim_type,
            "technologies": list(self.technologies),
        }


class SignalAdapter(ABC):
    name: str = "base"
    default_limit: int = 8

    @abstractmethod
    def fetch(self, limit: int | None = None) -> list[SignalRecord]:
        raise NotImplementedError
