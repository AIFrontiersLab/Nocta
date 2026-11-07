from types import SimpleNamespace

from app.services.export import ideas_to_csv, ideas_to_json
from app.services.timeline import normalize_stage, sort_events, timeline_summary


def test_ideas_export_roundtrip_shapes():
    ideas = [
        SimpleNamespace(
            id="idea_1",
            name="Agent Escrow",
            one_liner="Hold funds for agents",
            score=88,
            score_band="exceptional",
            status="winner",
            mode="missing-primitive",
        )
    ]
    js = ideas_to_json(ideas)
    csv = ideas_to_csv(ideas)
    assert "Agent Escrow" in js
    assert "idea_1" in csv
    assert csv.splitlines()[0].startswith("id,")


def test_timeline_helpers():
    assert normalize_stage("signal") == "signals"
    events = [
        SimpleNamespace(stage="report", occurred_at="2", message="done"),
        SimpleNamespace(stage="signals", occurred_at="1", message="start"),
    ]
    ordered = sort_events(events)
    assert ordered[0].stage == "signals"
    summary = timeline_summary(events)
    assert summary["event_count"] == 2
