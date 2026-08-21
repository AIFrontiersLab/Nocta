from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.serializers import evaluation_to_dict, idea_to_dict, prototype_to_dict
from app.database import get_db
from app.database.models import AgentEvaluation, Idea, IdeaScore, Prototype

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get("")
def list_ideas(status: str | None = Query(default=None), db: Session = Depends(get_db)):
    q = db.query(Idea).order_by(Idea.score.desc())
    if status and status != "all":
        if status == "exceptional":
            q = q.filter(Idea.score_band == "exceptional")
        elif status == "prototype_candidates":
            q = q.filter(Idea.score_band == "prototype_candidate")
        elif status == "resurrected":
            q = q.filter(Idea.resurrected.is_(True))
        elif status == "rejected":
            q = q.filter(Idea.status == "rejected")
        else:
            q = q.filter(Idea.status == status)
    rows = q.limit(200).all()
    return {"items": [idea_to_dict(i) for i in rows]}


@router.get("/{idea_id}")
def get_idea(idea_id: str, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(404, "idea not found")
    scores = db.query(IdeaScore).filter(IdeaScore.idea_id == idea_id).order_by(IdeaScore.scored_at.desc()).all()
    evals = db.query(AgentEvaluation).filter(AgentEvaluation.idea_id == idea_id).all()
    protos = db.query(Prototype).filter(Prototype.idea_id == idea_id).all()
    payload = idea_to_dict(idea, include_evaluations=True)
    payload["scorecards"] = [
        {
            "weighted_total": s.weighted_total,
            "band": s.band,
            "reason": s.reason,
            "evidence": s.evidence,
            "confidence": s.confidence,
            "dimensions": s.dimensions,
            "scored_at": s.scored_at.isoformat() if s.scored_at else None,
        }
        for s in scores
    ]
    payload["agent_debate"] = [evaluation_to_dict(e) for e in evals]
    payload["prototypes"] = [prototype_to_dict(p) for p in protos]
    return payload
