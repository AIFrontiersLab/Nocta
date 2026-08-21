from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.serializers import convergence_to_dict
from app.database import get_db
from app.database.models import Convergence

router = APIRouter(prefix="/convergences", tags=["convergences"])


@router.get("")
def list_convergences(db: Session = Depends(get_db)):
    rows = db.query(Convergence).order_by(Convergence.strength.desc()).limit(100).all()
    return {"items": [convergence_to_dict(c) for c in rows]}
