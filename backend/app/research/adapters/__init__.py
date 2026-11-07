from __future__ import annotations

from app.research.adapters.base import SignalAdapter, SignalRecord
from app.research.adapters.github import GitHubAdapter
from app.research.adapters.hackernews import HackerNewsAdapter
from app.research.adapters.papers import PapersAdapter

ADAPTERS: list[type[SignalAdapter]] = [GitHubAdapter, HackerNewsAdapter, PapersAdapter]


def default_adapters() -> list[SignalAdapter]:
    return [cls() for cls in ADAPTERS]


__all__ = [
    "ADAPTERS",
    "GitHubAdapter",
    "HackerNewsAdapter",
    "PapersAdapter",
    "SignalAdapter",
    "SignalRecord",
    "default_adapters",
]
