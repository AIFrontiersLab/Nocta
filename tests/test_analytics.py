from app.analytics.cost_tracker import CostTracker, estimate_call_cost
from app.analytics.metrics import RunMetrics, summarize_history
from app.analytics.trends import top_technologies


def test_estimate_call_cost_scales_with_tokens():
    cheap = estimate_call_cost(task="FAST", prompt_tokens=1000, completion_tokens=0)
    heavy = estimate_call_cost(task="HEAVY", prompt_tokens=1000, completion_tokens=0)
    assert heavy > cheap


def test_cost_tracker_budget():
    tracker = CostTracker(budget_usd=0.01)
    tracker.record(task="HEAVY", prompt_tokens=5000, completion_tokens=5000)
    assert tracker.total_usd > 0
    assert "by_task" in tracker.summary()


def test_summarize_history():
    metrics = [
        RunMetrics(run_id="a", status="ok", ideas_generated=10, winner_score=80, prototype_built=True),
        RunMetrics(run_id="b", status="ok", ideas_generated=6, winner_score=70, prototype_built=False),
    ]
    summary = summarize_history(metrics)
    assert summary["runs"] == 2
    assert summary["avg_winner_score"] == 75
    assert summary["prototype_rate"] == 0.5


def test_top_technologies():
    class Idea:
        def __init__(self, tech):
            self.technology_convergence = tech

    points = top_technologies([Idea(["Agents", "Payments"]), Idea(["Agents"])])
    assert points[0].label == "Agents"
    assert points[0].value == 2
