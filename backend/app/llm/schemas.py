from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SCORE_DIMENSIONS = [
    "novelty",
    "problem_severity",
    "market_potential",
    "why_now",
    "technical_feasibility",
    "competitive_white_space",
    "defensibility",
    "distribution_potential",
    "revenue_potential",
    "wow_factor",
    "prototypeability",
    "signal_confidence",
]

ClaimType = Literal["FACT", "INFERENCE", "SPECULATION"]
ScoreBand = Literal["archive", "interesting", "watch", "prototype_candidate", "exceptional"]


class DimensionScore(BaseModel):
    score: float = Field(ge=0, le=10)
    reason: str
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.6)


class Scorecard(BaseModel):
    dimensions: dict[str, DimensionScore]
    weighted_total: float = 0
    band: str = "archive"
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)
    confidence: float = 0.6


class IdeaDraft(BaseModel):
    name: str
    one_liner: str
    problem: str
    customer: str
    future_thesis: str = ""
    technology_convergence: list[str] = Field(default_factory=list)
    why_now: str = ""
    why_difficult_before: str = ""
    what_recently_changed: str = ""
    current_alternatives: list[str] = Field(default_factory=list)
    novelty: str = ""
    potential_moat: str = ""
    mvp: str = ""
    architecture: str = ""
    risks: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    why_may_win: str = ""
    why_may_fail: str = ""
    market: str = ""
    first_customer: str = ""
    product: str = ""
    assumptions: list[str] = Field(default_factory=list)
    signal_bias: float = 0.0


class IdeaBatch(BaseModel):
    ideas: list[IdeaDraft] = Field(default_factory=list)


class AgentTake(BaseModel):
    role: str
    stance: Literal["for", "against", "mixed", "destroy"] = "mixed"
    quote: str
    full_text: str
    confidence: float = Field(ge=0, le=1, default=0.6)
    score_hint: float | None = Field(default=None, ge=0, le=10)


class JudgeDecision(BaseModel):
    winner_name: str
    finalists: list[str] = Field(default_factory=list)
    decision: Literal["PROTOTYPE", "WATCH", "RESEARCH", "ARCHIVE"] = "WATCH"
    confidence: float = Field(ge=0, le=1, default=0.7)
    reasoning: str
    dissent: str = ""
    unexpected_insight: str = ""


class DimensionBundle(BaseModel):
    dimensions: dict[str, DimensionScore]


class AutoDiscoverChoice(BaseModel):
    mode: str
    reason: str
    hypothesis: str
    theme: str = ""


class ConvergenceDraft(BaseModel):
    title: str
    thesis: str
    nodes: list[str]
    why_connect: str
    consequences: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    strength: float = 6


class ArchitectureBrief(BaseModel):
    architecture: str
    mvp: str
    product: str
    first_customer: str
    stack: list[str] = Field(default_factory=list)
