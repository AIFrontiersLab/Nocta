from __future__ import annotations

from typing import Any, Iterable


STAGE_ORDER = [
    "signals",
    "convergences",
    "mode",
    "generation",
    "filters",
    "scoring",
    "debate",
    "judge",
    "prototype",
    "report",
]


def normalize_stage(stage: str) -> str:
    value = (stage or "").strip().lower()
    aliases = {
        "signal": "signals",
        "convergence": "convergences",
        "generate": "generation",
        "filter": "filters",
        "score": "scoring",
        "build": "prototype",
        "morning": "report",
    }
    return aliases.get(value, value)


def sort_events(events: Iterable[Any]) -> list[Any]:
    order = {name: idx for idx, name in enumerate(STAGE_ORDER)}

    def key(event: Any) -> tuple[int, str]:
        stage = normalize_stage(getattr(event, "stage", None) or (event.get("stage") if isinstance(event, dict) else "") or "")
        occurred = getattr(event, "occurred_at", None) or (event.get("occurred_at") if isinstance(event, dict) else "") or ""
        return (order.get(stage, 999), str(occurred))

    return sorted(list(events), key=key)


def timeline_summary(events: Iterable[Any]) -> dict[str, Any]:
    rows = list(events)
    stages = [normalize_stage(getattr(e, "stage", None) or (e.get("stage") if isinstance(e, dict) else "") or "") for e in rows]
    unique = []
    for stage in stages:
        if stage and stage not in unique:
            unique.append(stage)
    return {
        "event_count": len(rows),
        "stages_seen": unique,
        "completed_pipeline": all(s in unique for s in ("signals", "generation", "scoring", "report")),
    }
