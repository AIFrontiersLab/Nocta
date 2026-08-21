from __future__ import annotations

from datetime import datetime
from typing import Any

from app.database.models import (
    AgentEvaluation,
    Convergence,
    Idea,
    MemoryItem,
    Prototype,
    Run,
    Signal,
    TimelineEvent,
    UserFeedback,
)


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def run_to_dict(run: Run) -> dict[str, Any]:
    return {
        "id": run.id,
        "started_at": _dt(run.started_at),
        "finished_at": _dt(run.finished_at),
        "status": run.status,
        "mode": run.mode,
        "mode_reason": run.mode_reason,
        "hypothesis": run.hypothesis,
        "theme": run.theme,
        "signals_count": run.signals_count,
        "ideas_generated": run.ideas_generated,
        "ideas_rejected": run.ideas_rejected,
        "finalists_count": run.finalists_count,
        "winner_id": run.winner_id,
        "prototype_status": run.prototype_status,
        "runtime_seconds": run.runtime_seconds,
        "estimated_cost_usd": run.estimated_cost_usd,
        "model_calls": run.model_calls,
        "tokens_used": run.tokens_used,
        "output_dir": run.output_dir,
        "dry_run": run.dry_run,
        "is_demo": run.is_demo,
        "error": run.error,
        "unexpected_insight": run.unexpected_insight,
        "recommendation": run.recommendation,
        "morning_report": run.morning_report,
    }


def timeline_to_dict(event: TimelineEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "run_id": event.run_id,
        "occurred_at": _dt(event.occurred_at),
        "stage": event.stage,
        "message": event.message,
        "details": event.details or {},
        "agent": event.agent,
        "model": event.model,
        "duration_ms": event.duration_ms,
        "tokens": event.tokens,
        "cost_usd": event.cost_usd,
        "status": event.status,
        "retry_count": event.retry_count,
    }


def signal_to_dict(signal: Signal) -> dict[str, Any]:
    return {
        "id": signal.id,
        "title": signal.title,
        "category": signal.category,
        "source": signal.source,
        "source_url": signal.source_url,
        "published_at": signal.published_at,
        "collected_at": _dt(signal.collected_at),
        "summary": signal.summary,
        "evidence": signal.evidence or [],
        "novelty_score": signal.novelty_score,
        "momentum_score": signal.momentum_score,
        "confidence": signal.confidence,
        "tags": signal.tags or [],
        "claim_type": signal.claim_type,
        "technologies": signal.technologies or [],
        "run_id": signal.run_id,
        "is_demo": signal.is_demo,
    }


def convergence_to_dict(conv: Convergence) -> dict[str, Any]:
    return {
        "id": conv.id,
        "title": conv.title,
        "thesis": conv.thesis,
        "nodes": conv.nodes or [],
        "why_connect": conv.why_connect,
        "consequences": conv.consequences or [],
        "opportunities": conv.opportunities or [],
        "signal_ids": conv.signal_ids or [],
        "strength": conv.strength,
        "run_id": conv.run_id,
        "is_demo": conv.is_demo,
    }


def idea_to_dict(idea: Idea, *, include_evaluations: bool = False) -> dict[str, Any]:
    payload = {
        "id": idea.id,
        "slug": idea.slug,
        "name": idea.name,
        "one_liner": idea.one_liner,
        "problem": idea.problem,
        "customer": idea.customer,
        "future_thesis": idea.future_thesis,
        "technology_convergence": idea.technology_convergence or [],
        "why_now": idea.why_now,
        "why_difficult_before": idea.why_difficult_before,
        "what_recently_changed": idea.what_recently_changed,
        "current_alternatives": idea.current_alternatives or [],
        "novelty": idea.novelty,
        "potential_moat": idea.potential_moat,
        "mvp": idea.mvp,
        "architecture": idea.architecture,
        "risks": idea.risks or [],
        "unknowns": idea.unknowns or [],
        "why_may_win": idea.why_may_win,
        "why_may_fail": idea.why_may_fail,
        "market": idea.market,
        "first_customer": idea.first_customer,
        "product": idea.product,
        "mode": idea.mode,
        "status": idea.status,
        "score": idea.score,
        "score_band": idea.score_band,
        "confidence": idea.confidence,
        "rejection_reason": idea.rejection_reason,
        "original_score": idea.original_score,
        "resurrected": idea.resurrected,
        "run_id": idea.run_id,
        "signal_ids": idea.signal_ids or [],
        "convergence_id": idea.convergence_id,
        "is_demo": idea.is_demo,
        "is_winner": idea.is_winner,
        "created_at": _dt(idea.created_at),
        "updated_at": _dt(idea.updated_at),
    }
    if include_evaluations:
        payload["evaluations"] = [evaluation_to_dict(e) for e in idea.evaluations]
    return payload


def evaluation_to_dict(ev: AgentEvaluation) -> dict[str, Any]:
    return {
        "id": ev.id,
        "role": ev.role,
        "stance": ev.stance,
        "quote": ev.quote,
        "full_text": ev.full_text,
        "confidence": ev.confidence,
        "score_hint": ev.score_hint,
        "created_at": _dt(ev.created_at),
    }


def prototype_to_dict(proto: Prototype) -> dict[str, Any]:
    return {
        "id": proto.id,
        "idea_id": proto.idea_id,
        "run_id": proto.run_id,
        "name": proto.name,
        "status": proto.status,
        "stack": proto.stack or [],
        "local_path": proto.local_path,
        "launch_command": proto.launch_command,
        "architecture": proto.architecture,
        "readme": proto.readme,
        "github_url": getattr(proto, "github_url", "") or "",
        "tests_passed": proto.tests_passed,
        "duration_seconds": proto.duration_seconds,
        "screenshot": proto.screenshot,
        "critic_notes": proto.critic_notes,
        "is_demo": proto.is_demo,
        "created_at": _dt(proto.created_at),
    }


def memory_to_dict(item: MemoryItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "learning": item.learning,
        "evidence": item.evidence or [],
        "category": item.category,
        "created_at": _dt(item.created_at),
        "is_demo": item.is_demo,
    }


def feedback_to_dict(fb: UserFeedback) -> dict[str, Any]:
    return {
        "id": fb.id,
        "idea_id": fb.idea_id,
        "reaction": fb.reaction,
        "action": fb.action,
        "note": fb.note,
        "created_at": _dt(fb.created_at),
    }
