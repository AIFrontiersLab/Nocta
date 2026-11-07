from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.metrics import compute_run_metrics, summarize_history
from app.analytics.trends import build_score_trend, top_technologies
from app.database.models import Idea, Run, get_session_factory
from app.evaluation.harness import evaluate_filters

router = APIRouter(tags=["analytics"])


def get_db():
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


@router.get("/analytics/overview")
def analytics_overview(db: Session = Depends(get_db)):
    runs = db.query(Run).order_by(Run.created_at.desc()).limit(50).all()
    metrics = [compute_run_metrics(run) for run in runs]
    ideas = db.query(Idea).order_by(Idea.created_at.desc()).limit(200).all()
    return {
        "summary": summarize_history(metrics),
        "score_trend": [p.to_dict() for p in build_score_trend(runs)],
        "top_technologies": [p.to_dict() for p in top_technologies(ideas)],
        "recent_runs": [m.to_dict() for m in metrics[:12]],
    }


@router.get("/analytics/evaluation")
def analytics_evaluation():
    report = evaluate_filters()
    return report.to_dict()
