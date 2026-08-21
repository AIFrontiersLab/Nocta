from __future__ import annotations

from typing import Protocol

from app.llm.router import ModelRouter
from app.llm.schemas import IdeaDraft


class ModeContext:
    def __init__(
        self,
        *,
        theme: str,
        signals: list[dict],
        convergences: list[dict],
        prior_names: list[str],
        llm: ModelRouter | None,
        dry_run: bool,
    ) -> None:
        self.theme = theme
        self.signals = signals
        self.convergences = convergences
        self.prior_names = prior_names
        self.llm = llm
        self.dry_run = dry_run


class ExperimentMode(Protocol):
    id: str
    name: str
    question: str

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]: ...
