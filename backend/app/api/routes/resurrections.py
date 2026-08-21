from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.serializers import idea_to_dict
from app.database import get_db
from app.database.models import Idea, IdeaHistory
from app.memory.resurrection import evaluate_resurrections

router = APIRouter(prefix="/resurrections", tags=["resurrections"])


@router.get("")
def list_resurrections(db: Session = Depends(get_db)):
    rows = (
        db.query(Idea)
        .filter(Idea.resurrected.is_(True))
        .order_by(Idea.updated_at.desc())
        .limit(50)
        .all()
    )
    items = []
    for idea in rows:
        hist = (
            db.query(IdeaHistory)
            .filter(IdeaHistory.idea_id == idea.id, IdeaHistory.event == "resurrected")
            .order_by(IdeaHistory.occurred_at.desc())
            .first()
        )
        payload = idea_to_dict(idea)
        payload["resurrection"] = hist.payload if hist else {}
        items.append(payload)
    return {"items": items}


@router.post("/evaluate")
def reevaluate(db: Session = Depends(get_db)):
    results = evaluate_resurrections(db)
    db.commit()
    return {"items": results}
