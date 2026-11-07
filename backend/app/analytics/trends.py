from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass
class TrendPoint:
    label: str
    value: float
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if payload["meta"] is None:
            payload.pop("meta")
        return payload


def build_score_trend(runs: Iterable[Any], *, limit: int = 30) -> list[TrendPoint]:
    points: list[TrendPoint] = []
    for run in list(runs)[:limit]:
        score = getattr(run, "winner_score", None)
        if score is None:
            continue
        label = str(getattr(run, "created_at", getattr(run, "id", "")))
        points.append(
            TrendPoint(
                label=label[:19],
                value=float(score),
                meta={"run_id": str(getattr(run, "id", "")), "mode": str(getattr(run, "mode", ""))},
            )
        )
    return points


def top_technologies(ideas: Iterable[Any], *, limit: int = 12) -> list[TrendPoint]:
    counter: Counter[str] = Counter()
    for idea in ideas:
        tech = getattr(idea, "technology_convergence", None) or getattr(idea, "technologies", None) or []
        if isinstance(tech, str):
            tech = [t.strip() for t in tech.split(",") if t.strip()]
        for item in tech:
            if item:
                counter[str(item)] += 1
    return [TrendPoint(label=name, value=float(count)) for name, count in counter.most_common(limit)]
