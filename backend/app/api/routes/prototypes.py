from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.serializers import prototype_to_dict
from app.database import get_db
from app.database.models import Prototype

router = APIRouter(prefix="/prototypes", tags=["prototypes"])


@router.get("")
def list_prototypes(db: Session = Depends(get_db)):
    rows = db.query(Prototype).order_by(Prototype.created_at.desc()).limit(100).all()
    return {"items": [prototype_to_dict(p) for p in rows]}
