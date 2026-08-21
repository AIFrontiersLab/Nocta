from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.serializers import feedback_to_dict
from app.database import get_db
from app.database.models import Idea, UserFeedback
from app.utils.ids import new_id, utc_now

router = APIRouter(tags=["feedback"])


class FeedbackRequest(BaseModel):
    reaction: str
    action: str = ""
    note: str = ""


@router.post("/ideas/{idea_id}/feedback")
def add_feedback(idea_id: str, body: FeedbackRequest, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(404, "idea not found")
    fb = UserFeedback(
        id=new_id("fb"),
        idea_id=idea_id,
        reaction=body.reaction,
        action=body.action,
        note=body.note,
        created_at=utc_now(),
    )
    db.add(fb)
    db.commit()
    return feedback_to_dict(fb)
