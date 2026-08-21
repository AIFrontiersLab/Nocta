from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Idea, MemoryItem
from app.llm.schemas import IdeaDraft
from app.utils.ids import new_id, utc_now
from app.utils.similarity import idea_similarity


def fingerprint(idea: IdeaDraft | Idea) -> str:
    name = idea.name if isinstance(idea, Idea) else idea.name
    one = idea.one_liner if isinstance(idea, Idea) else idea.one_liner
    return f"{name} {one}".strip()


def find_duplicate(db: Session, draft: IdeaDraft, threshold: float) -> Idea | None:
    blob = fingerprint(draft)
    existing = db.query(Idea).all()
    best: tuple[float, Idea] | None = None
    for idea in existing:
        score = idea_similarity(blob, fingerprint(idea))
        if best is None or score > best[0]:
            best = (score, idea)
    if best and best[0] >= threshold:
        return best[1]
    return None


def filter_duplicates(
    db: Session, drafts: list[IdeaDraft], threshold: float
) -> tuple[list[IdeaDraft], list[tuple[IdeaDraft, Idea, float]]]:
    unique: list[IdeaDraft] = []
    dupes: list[tuple[IdeaDraft, Idea, float]] = []
    seen_local: list[IdeaDraft] = []
    for draft in drafts:
        local_hit = None
        for prev in seen_local:
            sim = idea_similarity(fingerprint(draft), fingerprint(prev))
            if sim >= threshold:
                local_hit = prev
                break
        if local_hit:
            continue
        prior = find_duplicate(db, draft, threshold)
        if prior:
            dupes.append((draft, prior, idea_similarity(fingerprint(draft), fingerprint(prior))))
            continue
        seen_local.append(draft)
        unique.append(draft)
    return unique, dupes


def record_learning(db: Session, learning: str, evidence: list[str], category: str = "pattern") -> MemoryItem:
    item = MemoryItem(id=new_id("mem"), learning=learning, evidence=evidence, category=category, created_at=utc_now())
    db.add(item)
    return item
