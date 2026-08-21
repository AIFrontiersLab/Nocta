from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config.settings import get_settings
from app.utils.ids import utc_now


class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    mode: Mapped[str] = mapped_column(String(64), default="auto")
    mode_reason: Mapped[str] = mapped_column(Text, default="")
    hypothesis: Mapped[str] = mapped_column(Text, default="")
    theme: Mapped[str] = mapped_column(String(200), default="")
    signals_count: Mapped[int] = mapped_column(Integer, default=0)
    ideas_generated: Mapped[int] = mapped_column(Integer, default=0)
    ideas_rejected: Mapped[int] = mapped_column(Integer, default=0)
    finalists_count: Mapped[int] = mapped_column(Integer, default=0)
    winner_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    prototype_status: Mapped[str] = mapped_column(String(32), default="not_started")
    runtime_seconds: Mapped[float] = mapped_column(Float, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0)
    model_calls: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    output_dir: Mapped[str] = mapped_column(String(500), default="")
    dry_run: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str] = mapped_column(Text, default="")
    morning_report: Mapped[str] = mapped_column(Text, default="")
    whatsapp_payload: Mapped[str] = mapped_column(Text, default="")
    unexpected_insight: Mapped[str] = mapped_column(Text, default="")
    recommendation: Mapped[str] = mapped_column(String(32), default="")

    events: Mapped[list[TimelineEvent]] = relationship(back_populates="run", cascade="all, delete-orphan")
    ideas: Mapped[list[Idea]] = relationship(back_populates="run")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    stage: Mapped[str] = mapped_column(String(64), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    agent: Mapped[str] = mapped_column(String(64), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="ok")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    run: Mapped[Run] = relationship(back_populates="events")


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    title: Mapped[str] = mapped_column(String(400))
    category: Mapped[str] = mapped_column(String(64), default="technology")
    source: Mapped[str] = mapped_column(String(120), default="")
    source_url: Mapped[str] = mapped_column(String(800), default="")
    published_at: Mapped[str] = mapped_column(String(64), default="")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    summary: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[list[Any]] = mapped_column(JSON, default=list)
    novelty_score: Mapped[float] = mapped_column(Float, default=0)
    momentum_score: Mapped[float] = mapped_column(Float, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    claim_type: Mapped[str] = mapped_column(String(24), default="FACT")
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Technology(Base):
    __tablename__ = "technologies"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(64), default="capability")
    momentum: Mapped[float] = mapped_column(Float, default=5)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Convergence(Base):
    __tablename__ = "convergences"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    thesis: Mapped[str] = mapped_column(Text, default="")
    nodes: Mapped[list[str]] = mapped_column(JSON, default=list)
    why_connect: Mapped[str] = mapped_column(Text, default="")
    consequences: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    signal_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    strength: Mapped[float] = mapped_column(Float, default=0)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), index=True)
    name: Mapped[str] = mapped_column(String(200))
    one_liner: Mapped[str] = mapped_column(Text, default="")
    problem: Mapped[str] = mapped_column(Text, default="")
    customer: Mapped[str] = mapped_column(Text, default="")
    future_thesis: Mapped[str] = mapped_column(Text, default="")
    technology_convergence: Mapped[list[str]] = mapped_column(JSON, default=list)
    why_now: Mapped[str] = mapped_column(Text, default="")
    why_difficult_before: Mapped[str] = mapped_column(Text, default="")
    what_recently_changed: Mapped[str] = mapped_column(Text, default="")
    current_alternatives: Mapped[list[str]] = mapped_column(JSON, default=list)
    novelty: Mapped[str] = mapped_column(Text, default="")
    potential_moat: Mapped[str] = mapped_column(Text, default="")
    mvp: Mapped[str] = mapped_column(Text, default="")
    architecture: Mapped[str] = mapped_column(Text, default="")
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    unknowns: Mapped[list[str]] = mapped_column(JSON, default=list)
    why_may_win: Mapped[str] = mapped_column(Text, default="")
    why_may_fail: Mapped[str] = mapped_column(Text, default="")
    market: Mapped[str] = mapped_column(Text, default="")
    first_customer: Mapped[str] = mapped_column(Text, default="")
    product: Mapped[str] = mapped_column(Text, default="")
    mode: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="generated")
    score: Mapped[float] = mapped_column(Float, default=0)
    score_band: Mapped[str] = mapped_column(String(32), default="archive")
    confidence: Mapped[float] = mapped_column(Float, default=0)
    rejection_reason: Mapped[str] = mapped_column(Text, default="")
    original_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    resurrected: Mapped[bool] = mapped_column(Boolean, default=False)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    signal_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    convergence_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    fingerprint: Mapped[str] = mapped_column(String(400), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    run: Mapped[Run | None] = relationship(back_populates="ideas")
    scores: Mapped[list[IdeaScore]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    evaluations: Mapped[list[AgentEvaluation]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    prototypes: Mapped[list[Prototype]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    feedback: Mapped[list[UserFeedback]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    history: Mapped[list[IdeaHistory]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    assumptions: Mapped[list[Assumption]] = relationship(back_populates="idea", cascade="all, delete-orphan")


class IdeaScore(Base):
    __tablename__ = "idea_scores"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"), index=True)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    dimensions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    weighted_total: Mapped[float] = mapped_column(Float, default=0)
    band: Mapped[str] = mapped_column(String(32), default="archive")
    reason: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    idea: Mapped[Idea] = relationship(back_populates="scores")


class AgentEvaluation(Base):
    __tablename__ = "agent_evaluations"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"), index=True)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(64))
    stance: Mapped[str] = mapped_column(String(32), default="mixed")
    quote: Mapped[str] = mapped_column(Text, default="")
    full_text: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0)
    score_hint: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    idea: Mapped[Idea] = relationship(back_populates="evaluations")


class Prototype(Base):
    __tablename__ = "prototypes"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"), index=True)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32), default="planned")
    stack: Mapped[list[str]] = mapped_column(JSON, default=list)
    local_path: Mapped[str] = mapped_column(String(600), default="")
    launch_command: Mapped[str] = mapped_column(String(300), default="")
    architecture: Mapped[str] = mapped_column(Text, default="")
    readme: Mapped[str] = mapped_column(Text, default="")
    github_url: Mapped[str] = mapped_column(String(600), default="")
    tests_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0)
    screenshot: Mapped[str] = mapped_column(String(600), default="")
    critic_notes: Mapped[str] = mapped_column(Text, default="")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    idea: Mapped[Idea] = relationship(back_populates="prototypes")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"), index=True)
    reaction: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(32), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    idea: Mapped[Idea] = relationship(back_populates="feedback")


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    learning: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list)
    category: Mapped[str] = mapped_column(String(64), default="pattern")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Assumption(Base):
    __tablename__ = "assumptions"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"), index=True)
    statement: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="untested")
    evidence: Mapped[str] = mapped_column(Text, default="")

    idea: Mapped[Idea] = relationship(back_populates="assumptions")


class IdeaHistory(Base):
    __tablename__ = "idea_history"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"), index=True)
    event: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    idea: Mapped[Idea] = relationship(back_populates="history")


class LabSetting(Base):
    __tablename__ = "lab_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        url = settings.database_url
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, echo=False, future=True, connect_args=connect_args)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
    return _SessionLocal


def reset_engine() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def _ensure_sqlite_columns(engine) -> None:
    """Additive SQLite migrations for columns added after first create_all."""
    url = str(engine.url)
    if not url.startswith("sqlite"):
        return
    patches = {
        "prototypes": [("github_url", "VARCHAR(600) DEFAULT ''")],
    }
    with engine.begin() as conn:
        for table, columns in patches.items():
            existing = {
                row[1]
                for row in conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
            }
            for col_name, col_type in columns:
                if col_name not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    _ensure_sqlite_columns(engine)


def get_db():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
