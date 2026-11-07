from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RunMetrics:
    run_id: str
    status: str
    ideas_generated: int = 0
    ideas_rejected: int = 0
    finalists: int = 0
    signals_analyzed: int = 0
    convergences: int = 0
    winner_score: float | None = None
    runtime_seconds: float = 0.0
    estimated_cost_usd: float = 0.0
    prototype_built: bool = False
    mode: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_run_metrics(run: Any, *, ideas: list[Any] | None = None, signals: int = 0, convergences: int = 0) -> RunMetrics:
    idea_rows = list(ideas or [])
    generated = len(idea_rows) or int(getattr(run, "ideas_generated", 0) or 0)
    rejected = sum(1 for i in idea_rows if getattr(i, "status", "") == "rejected")
    if not idea_rows:
        rejected = int(getattr(run, "ideas_rejected", 0) or 0)
    finalists = sum(1 for i in idea_rows if getattr(i, "status", "") in {"finalist", "winner", "prototype_candidate"})
    if not idea_rows:
        finalists = int(getattr(run, "finalists", 0) or 0)
    winner_score = getattr(run, "winner_score", None)
    if winner_score is None:
        scores = [float(getattr(i, "score", 0) or 0) for i in idea_rows]
        winner_score = max(scores) if scores else None
    return RunMetrics(
        run_id=str(getattr(run, "id", "")),
        status=str(getattr(run, "status", "")),
        ideas_generated=generated,
        ideas_rejected=rejected,
        finalists=finalists,
        signals_analyzed=signals or int(getattr(run, "signals_analyzed", 0) or 0),
        convergences=convergences or int(getattr(run, "convergences_found", 0) or 0),
        winner_score=float(winner_score) if winner_score is not None else None,
        runtime_seconds=float(getattr(run, "runtime_seconds", 0) or 0),
        estimated_cost_usd=float(getattr(run, "estimated_cost_usd", 0) or 0),
        prototype_built=bool(getattr(run, "prototype_built", False)),
        mode=str(getattr(run, "mode", "") or ""),
    )


def summarize_history(metrics: list[RunMetrics]) -> dict[str, Any]:
    if not metrics:
        return {
            "runs": 0,
            "avg_winner_score": None,
            "avg_ideas_generated": 0,
            "prototype_rate": 0.0,
            "total_estimated_cost_usd": 0.0,
        }
    scored = [m.winner_score for m in metrics if m.winner_score is not None]
    return {
        "runs": len(metrics),
        "avg_winner_score": round(sum(scored) / len(scored), 2) if scored else None,
        "avg_ideas_generated": round(sum(m.ideas_generated for m in metrics) / len(metrics), 2),
        "prototype_rate": round(sum(1 for m in metrics if m.prototype_built) / len(metrics), 3),
        "total_estimated_cost_usd": round(sum(m.estimated_cost_usd for m in metrics), 4),
    }
