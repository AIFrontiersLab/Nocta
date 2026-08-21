from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.database.models import Idea, IdeaHistory, IdeaScore, Signal
from app.llm.schemas import DimensionScore
from app.scoring.engine import compute_scorecard
from app.utils.ids import new_id, utc_now
from app.utils.logging import get_logger

log = get_logger("resurrection")


def _recent_signal_boost(db: Session, idea: Idea) -> float:
    blob = " ".join(idea.technology_convergence or []).lower() + " " + idea.name.lower()
    cutoff = datetime.now(timezone.utc) - timedelta(days=45)
    recent = db.query(Signal).filter(Signal.collected_at >= cutoff).all()
    hits = 0
    momentum = 0.0
    for sig in recent:
        text = f"{sig.title} {sig.summary} {' '.join(sig.tags or [])}".lower()
        if any(tok in text for tok in blob.split() if len(tok) > 3):
            hits += 1
            momentum += sig.momentum_score or 0
    if hits == 0:
        return 0.0
    return min(2.4, 0.35 * hits + 0.08 * momentum)


def resurrection_candidates(db: Session) -> list[Idea]:
    return (
        db.query(Idea)
        .filter(Idea.status.in_(["archive", "rejected", "interesting", "watch"]))
        .filter(Idea.is_winner.is_(False))
        .all()
    )


def evaluate_resurrections(db: Session) -> list[dict]:
    settings = get_settings()
    results = []
    for idea in resurrection_candidates(db):
        boost = _recent_signal_boost(db, idea)
        if boost < 0.8:
            continue
        latest = (
            db.query(IdeaScore).filter(IdeaScore.idea_id == idea.id).order_by(IdeaScore.scored_at.desc()).first()
        )
        if not latest or not latest.dimensions:
            continue
        dims = {}
        for key, raw in latest.dimensions.items():
            dim = DimensionScore.model_validate(raw)
            if key in {"why_now", "signal_confidence", "novelty"}:
                dim.score = min(10.0, dim.score + boost)
                dim.reason = dim.reason + f" Resurrection boost +{boost:.1f} from new signals."
            dims[key] = dim
        card = compute_scorecard(dims, settings=settings, extra_reason="Resurrection re-score")
        delta = card.weighted_total - (idea.original_score or idea.score or 0)
        if delta < settings.resurrection_min_delta:
            continue
        idea.resurrected = True
        idea.status = "resurrected"
        previous = idea.score
        if idea.original_score is None:
            idea.original_score = previous
        idea.score = card.weighted_total
        idea.score_band = card.band
        db.add(
            IdeaScore(
                id=new_id("scr"),
                idea_id=idea.id,
                dimensions={k: v.model_dump() for k, v in card.dimensions.items()},
                weighted_total=card.weighted_total,
                band=card.band,
                reason=card.reason,
                evidence=card.evidence + [f"signal boost {boost:.2f}"],
                confidence=card.confidence,
            )
        )
        db.add(
            IdeaHistory(
                id=new_id("hst"),
                idea_id=idea.id,
                event="resurrected",
                payload={
                    "original": idea.original_score,
                    "current": card.weighted_total,
                    "delta": round(delta, 1),
                    "boost": boost,
                },
                occurred_at=utc_now(),
            )
        )
        results.append(
            {
                "id": idea.id,
                "name": idea.name,
                "original_score": idea.original_score,
                "current_score": card.weighted_total,
                "delta": round(delta, 1),
                "what_changed": [
                    "New related signals increased why-now and confidence",
                    f"Resurrection boost {boost:.1f} from recent activity",
                ],
            }
        )
        log.stage("idea resurrected", name=idea.name, delta=round(delta, 1))
    return results
