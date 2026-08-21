from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.serializers import memory_to_dict
from app.database import get_db
from app.database.models import Convergence, Idea, MemoryItem, Prototype, Run, Signal

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("")
def memory(db: Session = Depends(get_db)):
    learnings = db.query(MemoryItem).order_by(MemoryItem.created_at.desc()).limit(30).all()
    return {
        "metrics": {
            "ideas_generated": db.query(Idea).count(),
            "experiments": db.query(Run).count(),
            "signals": db.query(Signal).count(),
            "convergences": db.query(Convergence).count(),
            "rejected_ideas": db.query(Idea).filter(Idea.status == "rejected").count(),
            "prototypes": db.query(Prototype).count(),
            "resurrected_ideas": db.query(Idea).filter(Idea.resurrected.is_(True)).count(),
        },
        "learnings": [memory_to_dict(item) for item in learnings],
    }
