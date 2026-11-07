from app.evaluation.baselines import baseline_names
from app.evaluation.harness import evaluate_filters


def test_baseline_catalog_not_empty():
    assert len(baseline_names()) >= 4


def test_evaluate_filters_runs():
    report = evaluate_filters()
    assert report.suite == "obvious_filter_baselines"
    assert report.passed + report.failed == len(report.cases)
    payload = report.to_dict()
    assert "ok" in payload
