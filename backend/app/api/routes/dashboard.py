from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.serializers import convergence_to_dict, idea_to_dict, run_to_dict, signal_to_dict
from app.database import get_db
from app.database.models import Convergence, Idea, Run, Signal

router = APIRouter(tags=["dashboard"])


@router.get("/home")
def home(db: Session = Depends(get_db)):
    latest_run = db.query(Run).order_by(Run.started_at.desc()).first()
    winner = None
    if latest_run and latest_run.winner_id:
        winner = db.query(Idea).filter(Idea.id == latest_run.winner_id).first()
    if not winner:
        winner = db.query(Idea).filter(Idea.is_winner.is_(True)).order_by(Idea.created_at.desc()).first()
    recent_signals = db.query(Signal).order_by(Signal.collected_at.desc()).limit(6).all()
    convergences = db.query(Convergence).order_by(Convergence.strength.desc()).limit(6).all()
    return {
        "hero": {
            "greeting": "GOOD MORNING.",
            "subtitle": "FutureLab explored the frontier while you slept.",
            "winner": idea_to_dict(winner) if winner else None,
            "run": run_to_dict(latest_run) if latest_run else None,
        },
        "stats": {
            "tonights_experiment": latest_run.mode if latest_run else "—",
            "signals_analyzed": latest_run.signals_count if latest_run else 0,
            "ideas_generated": latest_run.ideas_generated if latest_run else 0,
            "ideas_rejected": latest_run.ideas_rejected if latest_run else 0,
            "finalists": latest_run.finalists_count if latest_run else 0,
            "prototype_status": latest_run.prototype_status if latest_run else "not_started",
            "runtime": latest_run.runtime_seconds if latest_run else 0,
            "estimated_cost": latest_run.estimated_cost_usd if latest_run else 0,
        },
        "reasoning_chain": _reasoning_chain(latest_run, winner, recent_signals, convergences),
        "signals": [signal_to_dict(s) for s in recent_signals],
        "convergences": [convergence_to_dict(c) for c in convergences],
    }


def _reasoning_chain(run: Run | None, winner: Idea | None, signals: list[Signal], convergences: list[Convergence]):
    chain = []
    for sig in signals[:2]:
        chain.append({"type": "signal", "label": sig.title, "id": sig.id})
    if convergences:
        chain.append({"type": "convergence", "label": convergences[0].title, "id": convergences[0].id})
    if winner:
        chain.append({"type": "opportunity", "label": winner.problem[:120], "id": winner.id})
        chain.append({"type": "invention", "label": winner.name, "id": winner.id})
    if run:
        chain.insert(0, {"type": "experiment", "label": run.mode_reason or run.mode, "id": run.id})
    return chain
