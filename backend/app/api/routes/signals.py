from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.serializers import signal_to_dict
from app.database import get_db
from app.database.models import Signal

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
def list_signals(
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(Signal).order_by(Signal.collected_at.desc())
    if category and category != "all":
        q = q.filter(Signal.category == category)
    rows = q.limit(200).all()
    return {"items": [signal_to_dict(s) for s in rows]}
