from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.agents.team import debate_idea, judge_finalists, score_dimensions_for_idea
from app.builder.prototype import build_prototype
from app.config.settings import Settings, get_settings
from app.database.models import (
    AgentEvaluation,
    Assumption,
    Convergence,
    Idea,
    IdeaHistory,
    IdeaScore,
    Prototype,
    Run,
    Signal,
    TimelineEvent,
    get_session_factory,
    init_db,
)
from app.llm.router import ModelRouter, RunBudget
from app.llm.schemas import IdeaDraft
from app.memory.resurrection import evaluate_resurrections
from app.memory.store import filter_duplicates, fingerprint, record_learning
from app.modes.base import ModeContext
from app.modes.registry import choose_auto_mode, resolve_mode
from app.research.convergence import detect_convergences
from app.research.signals import collect_signals
from app.scoring.engine import compute_scorecard, recommendation_for_band
from app.scoring.obvious import is_impossible, is_obvious
from app.scoring.domain import enforce_ai_theme, is_ai_agentic_scope, signal_is_ai_agentic
from app.orchestration.result import ExperimentResult
from app.services.notifier import MorningNotifier
from app.services.reporter import morning_report_markdown, whatsapp_payload, write_run_artifacts
from app.utils.ids import new_id, utc_now
from app.utils.logging import get_logger, setup_logging

log = get_logger("pipeline")


def emit(db: Session, run: Run, stage: str, message: str, **details) -> None:
    event = TimelineEvent(
        id=new_id("evt"),
        run_id=run.id,
        occurred_at=utc_now(),
        stage=stage,
        message=message,
        details=details,
        agent=str(details.get("agent", "")),
        model=str(details.get("model", "")),
        duration_ms=int(details.get("duration_ms") or 0),
        tokens=int(details.get("tokens") or 0),
        cost_usd=float(details.get("cost_usd") or 0),
        status=str(details.get("status") or "ok"),
        retry_count=int(details.get("retry_count") or 0),
    )
    db.add(event)
    db.commit()
    log.stage(message, run=run.id, stage=stage)


def _select_build_ideas(
    winner: Idea | None,
    finalists: list[tuple[Idea, IdeaDraft, float]],
    count: int,
) -> list[Idea]:
    """Pick winner first, then next-highest finalists, up to ``count`` ideas."""
    targets: list[Idea] = []
    seen: set[str] = set()
    if winner:
        targets.append(winner)
        seen.add(winner.id)
    ranked = sorted(finalists, key=lambda row: row[2], reverse=True)
    for idea, _, _ in ranked:
        if len(targets) >= count:
            break
        if idea.id in seen:
            continue
        targets.append(idea)
        seen.add(idea.id)
    return targets[:count]


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")[:60]


def _persist_signals(db: Session, run: Run, raw: list[dict]) -> list[Signal]:
    rows = []
    for item in raw:
        row = Signal(
            id=item.get("id") or new_id("sig"),
            title=item["title"],
            category=item.get("category") or "technology",
            source=item.get("source") or "",
            source_url=item.get("source_url") or "",
            published_at=item.get("published_at") or "",
            collected_at=utc_now(),
            summary=item.get("summary") or "",
            evidence=item.get("evidence") or [],
            novelty_score=float(item.get("novelty_score") or 0),
            momentum_score=float(item.get("momentum_score") or 0),
            confidence=float(item.get("confidence") or 0),
            tags=item.get("tags") or [],
            claim_type=item.get("claim_type") or "FACT",
            technologies=item.get("technologies") or [],
            run_id=run.id,
            is_demo=False,
        )
        db.add(row)
        rows.append(row)
        item["id"] = row.id
    db.commit()
    return rows


def _persist_convergences(db: Session, run: Run, raw: list[dict]) -> list[Convergence]:
    rows = []
    for item in raw:
        row = Convergence(
            id=item.get("id") or new_id("cvg"),
            title=item["title"],
            thesis=item.get("thesis") or "",
            nodes=item.get("nodes") or [],
            why_connect=item.get("why_connect") or "",
            consequences=item.get("consequences") or [],
            opportunities=item.get("opportunities") or [],
            signal_ids=item.get("signal_ids") or [],
            strength=float(item.get("strength") or 0),
            run_id=run.id,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    return rows


def _persist_idea(db: Session, run: Run, draft: IdeaDraft, *, status: str, mode: str) -> Idea:
    idea = Idea(
        id=new_id("idea"),
        slug=_slug(draft.name),
        name=draft.name,
        one_liner=draft.one_liner,
        problem=draft.problem,
        customer=draft.customer,
        future_thesis=draft.future_thesis,
        technology_convergence=draft.technology_convergence,
        why_now=draft.why_now,
        why_difficult_before=draft.why_difficult_before,
        what_recently_changed=draft.what_recently_changed,
        current_alternatives=draft.current_alternatives,
        novelty=draft.novelty,
        potential_moat=draft.potential_moat,
        mvp=draft.mvp,
        architecture=draft.architecture,
        risks=draft.risks,
        unknowns=draft.unknowns,
        why_may_win=draft.why_may_win,
        why_may_fail=draft.why_may_fail,
        market=draft.market,
        first_customer=draft.first_customer,
        product=draft.product,
        mode=mode,
        status=status,
        fingerprint=fingerprint(draft),
        run_id=run.id,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(idea)
    for statement in draft.assumptions:
        db.add(Assumption(id=new_id("asm"), idea_id=idea.id, statement=statement))
    db.commit()
    db.refresh(idea)
    return idea


def run_experiment(
    *,
    mode: str = "auto",
    theme: str = "",
    dry_run: bool = False,
    build: bool = False,
    settings: Settings | None = None,
    session: Session | None = None,
) -> ExperimentResult:
    s = settings or get_settings()
    setup_logging(s.log_level)
    init_db()
    own_session = session is None
    db = session or get_session_factory()()
    started = time.monotonic()
    run = Run(
        id=new_id("run"),
        started_at=utc_now(),
        status="running",
        mode=mode,
        theme=theme,
        dry_run=dry_run,
    )
    db.add(run)
    db.commit()

    day = date.today().isoformat()
    out_dir = s.resolved_output_dir / day / run.id
    for folder in ("report", "research", "signals", "ideas", "winner", "architecture", "prototype", "screenshots", "logs"):
        (out_dir / folder).mkdir(parents=True, exist_ok=True)
    run.output_dir = str(out_dir)
    db.commit()

    budget = RunBudget(s.max_model_calls, s.max_tokens, s.max_runtime_minutes * 60)
    llm: ModelRouter | None = None
    if not dry_run:
        candidate = ModelRouter(budget=budget)
        if candidate.available():
            llm = candidate
        else:
            log.warning("LLM unavailable; continuing with structured catalog + scoring")
            dry_run = False  # still a real run, just without LLM
            run.dry_run = False

    try:
        emit(db, run, "start", "Signal discovery started")
        live_signals = collect_signals(max_queries=s.max_research_queries, live=not dry_run)
        if s.require_ai_agentic_scope and live_signals:
            scoped = [sig for sig in live_signals if signal_is_ai_agentic(sig)]
            if scoped:
                live_signals = scoped
        if not live_signals:
            live_signals = _fixture_agent_signals()
            emit(db, run, "signals", "Live sources unavailable or empty; using labeled lab fixtures", status="degraded")
        _persist_signals(db, run, live_signals)
        run.signals_count = len(live_signals)
        db.commit()
        (out_dir / "signals" / "signals.json").write_text(json.dumps(live_signals, indent=2, default=str), encoding="utf-8")
        emit(db, run, "signals", f"{len(live_signals)} signals processed")

        convergences = detect_convergences(live_signals)
        _persist_convergences(db, run, convergences)
        emit(db, run, "convergences", f"{len(convergences)} unusual convergences detected")
        (out_dir / "research" / "convergences.json").write_text(json.dumps(convergences, indent=2), encoding="utf-8")

        recent_modes = [r.mode for r in db.query(Run).order_by(Run.started_at.desc()).limit(8).all() if r.id != run.id]
        signal_blob = " ".join(f"{x.get('title')} {x.get('summary')}" for x in live_signals)
        requested = mode
        if requested in {"auto", "auto-discover", ""}:
            chosen, reason, hypothesis, auto_theme = choose_auto_mode(recent_modes, signal_blob)
            run.mode = chosen
            run.mode_reason = reason
            run.hypothesis = hypothesis
            run.theme = enforce_ai_theme(theme or auto_theme) if s.require_ai_agentic_scope else (theme or auto_theme)
        else:
            resolved = resolve_mode(requested)
            run.mode = resolved.id
            run.mode_reason = f"User selected {resolved.name}"
            run.hypothesis = resolved.question
            run.theme = enforce_ai_theme(theme or resolved.name) if s.require_ai_agentic_scope else (theme or resolved.name)
        db.commit()
        emit(db, run, "mode", f"Tonight's experiment: {run.mode}", reason=run.mode_reason)

        mode_obj = resolve_mode(run.mode)
        prior_names = [i.name for i in db.query(Idea).all()]
        ctx = ModeContext(
            theme=run.theme,
            signals=live_signals,
            convergences=convergences,
            prior_names=prior_names,
            llm=llm,
            dry_run=dry_run,
        )
        drafts = mode_obj.generate(ctx)
        emit(db, run, "generate", f"{len(drafts)} candidate inventions generated")

        unique, dupes = filter_duplicates(db, drafts, s.duplicate_similarity_threshold)
        rejected = 0
        kept: list[tuple[IdeaDraft, dict]] = []
        for draft in unique:
            blob = f"{draft.name} {draft.one_liner} {draft.product}"
            if s.require_ai_agentic_scope:
                in_scope, scope_why = is_ai_agentic_scope(
                    name=draft.name,
                    one_liner=draft.one_liner,
                    problem=draft.problem,
                    product=draft.product,
                    customer=draft.customer,
                    theme=run.theme,
                    technology_convergence=list(draft.technology_convergence or []),
                )
                if not in_scope:
                    idea = _persist_idea(db, run, draft, status="rejected", mode=run.mode)
                    idea.rejection_reason = scope_why
                    rejected += 1
                    continue
            obvious, why = is_obvious(blob)
            impossible, why_i = is_impossible(blob)
            if obvious or impossible:
                idea = _persist_idea(db, run, draft, status="rejected", mode=run.mode)
                idea.rejection_reason = why or why_i
                rejected += 1
                continue
            kept.append((draft, getattr(draft, "__dict__", {})))

        for draft, prior, sim in dupes:
            idea = _persist_idea(db, run, draft, status="rejected", mode=run.mode)
            idea.rejection_reason = f"Duplicate of {prior.name} (similarity {sim:.2f})"
            rejected += 1
        db.commit()
        emit(db, run, "filter", f"{rejected} rejected after AI-scope/obvious/impossible/duplicate filters")

        scored_rows: list[tuple[Idea, IdeaDraft, float]] = []
        for draft, _meta in kept:
            idea = _persist_idea(db, run, draft, status="generated", mode=run.mode)
            bias = float(draft.signal_bias or 0.0)
            sig_conf = min(9.5, 5.5 + (sum(s.get("confidence", 0) for s in live_signals) / max(1, len(live_signals))) * 3)
            bundle = score_dimensions_for_idea(
                draft, signal_confidence=sig_conf, novelty_bonus=bias, llm=llm
            )
            card = compute_scorecard(bundle.dimensions, settings=s)
            idea.score = card.weighted_total
            idea.score_band = card.band
            idea.confidence = card.confidence
            idea.status = card.band
            db.add(
                IdeaScore(
                    id=new_id("scr"),
                    idea_id=idea.id,
                    run_id=run.id,
                    dimensions={k: v.model_dump() for k, v in card.dimensions.items()},
                    weighted_total=card.weighted_total,
                    band=card.band,
                    reason=card.reason,
                    evidence=card.evidence,
                    confidence=card.confidence,
                )
            )
            db.add(
                IdeaHistory(
                    id=new_id("hst"),
                    idea_id=idea.id,
                    event="scored",
                    payload={"score": card.weighted_total, "band": card.band},
                )
            )
            scored_rows.append((idea, draft, card.weighted_total))
        db.commit()

        scored_rows.sort(key=lambda row: row[2], reverse=True)
        # Internally we may have ~8-20; keep 5 finalists for debate. Do not show 100 on the UI.
        finalists = scored_rows[:5]
        for idea, _, _ in scored_rows[5:]:
            if idea.status not in {"rejected"}:
                idea.status = idea.score_band or "archive"
        for idea, _, _ in finalists:
            idea.status = "finalist"
        db.commit()
        emit(db, run, "finalists", f"{len(finalists)} finalists selected")

        debates: dict[str, list] = {}
        for idea, draft, _ in finalists:
            takes = debate_idea(draft, llm)
            debates[draft.name] = takes
            for take in takes:
                db.add(
                    AgentEvaluation(
                        id=new_id("eval"),
                        idea_id=idea.id,
                        run_id=run.id,
                        role=take.role,
                        stance=take.stance,
                        quote=take.quote,
                        full_text=take.full_text,
                        confidence=take.confidence,
                        score_hint=take.score_hint,
                    )
                )
        db.commit()
        emit(db, run, "debate", "Agent debate completed")

        drafts_by_name = {d.name: d for _, d, _ in finalists}
        ideas_by_name = {i.name: i for i, _, _ in finalists}
        scores = {i.name: sc for i, _, sc in finalists}
        decision = judge_finalists([d for _, d, _ in finalists], debates, scores, llm)
        winner_idea = ideas_by_name.get(decision.winner_name) or (finalists[0][0] if finalists else None)
        winner_draft = drafts_by_name.get(decision.winner_name) if winner_idea else None
        if winner_idea:
            winner_idea.is_winner = True
            winner_idea.status = "winner"
            run.winner_id = winner_idea.id
            run.unexpected_insight = decision.unexpected_insight or (
                "The judge did not average away dissent; sequencing of primitives may matter more than any single product."
            )
            rec = recommendation_for_band(winner_idea.score_band)
            if decision.decision == "PROTOTYPE":
                rec = "BUILD"
            run.recommendation = rec
            db.add(
                AgentEvaluation(
                    id=new_id("eval"),
                    idea_id=winner_idea.id,
                    run_id=run.id,
                    role="judge",
                    stance="for",
                    quote=f"Decision: {decision.decision} · confidence {int(decision.confidence*100)}%",
                    full_text=decision.reasoning + "\n" + (decision.dissent or ""),
                    confidence=decision.confidence,
                )
            )
        db.commit()
        emit(db, run, "winner", f"Winner selected: {winner_idea.name if winner_idea else 'none'}")

        prototypes: list[Prototype] = []
        build_count = max(1, int(s.daily_prototype_count or 1))
        build_ideas = _select_build_ideas(winner_idea, finalists, build_count)
        if winner_idea:
            (out_dir / "winner" / "winner.json").write_text(
                json.dumps(
                    {
                        "name": winner_idea.name,
                        "score": winner_idea.score,
                        "why_now": winner_idea.why_now,
                        "decision": decision.model_dump(),
                        "build_targets": [
                            {"name": idea.name, "score": idea.score, "slot": idx}
                            for idx, idea in enumerate(build_ideas, start=1)
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (out_dir / "architecture" / "architecture.md").write_text(
                f"# {winner_idea.name}\n\n{winner_idea.architecture}\n\n## MVP\n{winner_idea.mvp}\n",
                encoding="utf-8",
            )
            emit(db, run, "architecture", "Architecture generated")
            should_build = build or (
                s.auto_prototype
                and bool(build_ideas)
                and (build_ideas[0].score or 0) >= s.prototype_threshold
                and not s.require_human_approval_for_build
            )
            if should_build or (build and s.require_human_approval_for_build):
                emit(db, run, "prototype", f"Building {len(build_ideas)} prototype(s) for daily GitHub publish")
                for slot, idea in enumerate(build_ideas, start=1):
                    if slot > 1 and idea.id != (winner_idea.id if winner_idea else None):
                        if idea.status not in {"winner", "rejected"}:
                            idea.status = "runner_up"
                    proto = build_prototype(idea, out_dir, approved=build or should_build, slot=slot)
                    proto.run_id = run.id
                    db.add(proto)
                    prototypes.append(proto)
                    emit(
                        db,
                        run,
                        "prototype",
                        f"Prototype {slot}/{len(build_ideas)} {proto.status}: {idea.name}",
                        github=proto.github_url or "",
                    )
                run.prototype_status = prototypes[-1].status if prototypes else "not_started"
                if any(p.github_url for p in prototypes):
                    run.prototype_status = "published"
                db.commit()
            else:
                run.prototype_status = (
                    "awaiting_approval"
                    if build_ideas and (build_ideas[0].score or 0) >= s.prototype_threshold
                    else "not_started"
                )
                db.commit()

        evaluate_resurrections(db)
        if winner_idea:
            record_learning(
                db,
                f"{winner_idea.mode} selected {winner_idea.name} because why-now and novelty survived dissent.",
                [f"run:{run.id}", f"score:{winner_idea.score}"],
                "selection",
            )
            record_learning(
                db,
                "Ideas differentiated only by wrapping a chatbot rarely survive scoring caps on novelty.",
                ["obvious-filter", "novelty cap < 4 → max 64"],
                "pattern",
            )
        db.commit()

        report = morning_report_markdown(run, winner_idea, prototypes)
        payload = whatsapp_payload(run, winner_idea, prototypes)
        run.morning_report = report
        run.whatsapp_payload = payload
        write_run_artifacts(out_dir, report, payload)
        deliveries = MorningNotifier(s).collect_deliveries(payload)

        run.ideas_generated = len(drafts)
        run.ideas_rejected = rejected + len(dupes)
        run.finalists_count = len(finalists)
        run.model_calls = budget.calls
        run.tokens_used = budget.tokens
        run.estimated_cost_usd = (
            0.0 if s.uses_shared_route else round(budget.tokens / 1_000_000 * 3.0, 4)
        )
        run.runtime_seconds = round(time.monotonic() - started, 2)
        run.finished_at = utc_now()
        run.status = "completed"
        db.commit()
        emit(db, run, "complete", "FutureLab run complete")
        db.refresh(run)
        return ExperimentResult(run=run, deliveries=deliveries)
    except Exception as exc:
        log.exception("run failed")
        run.status = "failed"
        run.error = str(exc)
        run.finished_at = utc_now()
        run.runtime_seconds = round(time.monotonic() - started, 2)
        db.commit()
        emit(db, run, "error", f"Run failed: {exc}", status="error")
        db.refresh(run)
        return ExperimentResult(run=run, deliveries=[])
    finally:
        if own_session:
            db.close()


def _fixture_agent_signals() -> list[dict]:
    """Labeled lab fixtures used only when live sources return nothing. Not fake news."""
    return [
        {
            "id": new_id("sig"),
            "title": "Lab fixture: agent-to-agent checkout experiments",
            "category": "market",
            "source": "FutureLab Lab Fixture",
            "source_url": "",
            "published_at": "",
            "summary": "Illustrative cluster: multiple teams are prototyping machine-payable APIs. Not a real article.",
            "evidence": ["lab-fixture"],
            "novelty_score": 7.2,
            "momentum_score": 7.8,
            "confidence": 0.45,
            "tags": ["agent-commerce", "payments", "fixture"],
            "claim_type": "SPECULATION",
            "technologies": ["Agent Commerce", "Stablecoins", "Agent Identity"],
        },
        {
            "id": new_id("sig"),
            "title": "Lab fixture: agent identity / authorization discussions",
            "category": "technology",
            "source": "FutureLab Lab Fixture",
            "source_url": "",
            "published_at": "",
            "summary": "Illustrative cluster: identity for non-human actors is being designed in several stacks at once.",
            "evidence": ["lab-fixture"],
            "novelty_score": 7.0,
            "momentum_score": 7.4,
            "confidence": 0.45,
            "tags": ["identity", "authorization", "fixture"],
            "claim_type": "SPECULATION",
            "technologies": ["Agent Identity", "Authorization"],
        },
        {
            "id": new_id("sig"),
            "title": "Lab fixture: computer-use agents on legacy GUIs",
            "category": "developer",
            "source": "FutureLab Lab Fixture",
            "source_url": "",
            "published_at": "",
            "summary": "Illustrative cluster: operators for software without APIs.",
            "evidence": ["lab-fixture"],
            "novelty_score": 6.8,
            "momentum_score": 7.0,
            "confidence": 0.4,
            "tags": ["computer-use", "fixture"],
            "claim_type": "SPECULATION",
            "technologies": ["Computer Use", "Legacy Enterprise"],
        },
    ]
