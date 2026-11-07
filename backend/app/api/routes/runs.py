from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.serializers import idea_to_dict, run_to_dict, timeline_to_dict
from app.database import get_db, get_session_factory
from app.database.models import Idea, Run, TimelineEvent
from app.modes.registry import ALL_MODES
from app.orchestration.pipeline import run_experiment

router = APIRouter(tags=["experiments", "runs"])


class StartRunRequest(BaseModel):
    mode: str = "auto"
    theme: str = ""
    dry_run: bool = False
    build: bool = False


def _background_run(mode: str, theme: str, dry_run: bool, build: bool) -> None:
    db = get_session_factory()()
    try:
        run_experiment(mode=mode, theme=theme, dry_run=dry_run, build=build, session=db)
        # Deliveries are returned to remote Hermes on the Mac mini; API runs are fire-and-forget.
    finally:
        db.close()


@router.get("/modes")
def list_modes():
    return {
        "items": [
            {"id": m.id, "name": m.name, "question": m.question}
            for m in ALL_MODES
            if m.id != "auto"
        ]
    }


@router.post("/runs/start")
def start_run(body: StartRunRequest, background: BackgroundTasks):
    background.add_task(_background_run, body.mode, body.theme, body.dry_run, body.build)
    return {"status": "queued", "mode": body.mode}


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    rows = db.query(Run).order_by(Run.started_at.desc()).limit(50).all()
    return {"items": [run_to_dict(r) for r in rows]}


@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(404, "run not found")
    events = (
        db.query(TimelineEvent).filter(TimelineEvent.run_id == run_id).order_by(TimelineEvent.occurred_at.asc()).all()
    )
    ideas = db.query(Idea).filter(Idea.run_id == run_id).order_by(Idea.score.desc()).all()
    return {
        "run": run_to_dict(run),
        "timeline": [timeline_to_dict(e) for e in events],
        "ideas": [idea_to_dict(i) for i in ideas],
    }
