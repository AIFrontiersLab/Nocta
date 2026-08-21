from __future__ import annotations

from datetime import timedelta

from app.database import get_session_factory, init_db
from app.database.models import (
    AgentEvaluation,
    Convergence,
    Idea,
    IdeaHistory,
    IdeaScore,
    MemoryItem,
    Prototype,
    Run,
    Signal,
    TimelineEvent,
)
from app.utils.ids import new_id, utc_now


def seed_demo_data() -> None:
    init_db()
    db = get_session_factory()()
    try:
        if db.query(Run).filter(Run.is_demo.is_(True)).first():
            return

        now = utc_now()
        run = Run(
            id=new_id("run"),
            started_at=now - timedelta(hours=5),
            finished_at=now - timedelta(hours=2, minutes=41),
            status="completed",
            mode="missing-primitive",
            mode_reason="Agent-to-agent commerce appeared independently across 6 recent signals.",
            hypothesis="Autonomous agents may need transaction trust infrastructure before mass adoption.",
            theme="Autonomous AI Agents",
            signals_count=317,
            ideas_generated=96,
            ideas_rejected=76,
            finalists_count=5,
            prototype_status="built",
            runtime_seconds=4 * 3600 + 48 * 60,
            estimated_cost_usd=0.0,
            model_calls=42,
            tokens_used=118000,
            output_dir="outputs/futurelab/demo",
            is_demo=True,
            unexpected_insight="Agent reputation may become important before agent credit.",
            recommendation="BUILD",
        )
        db.add(run)

        signal_rows = [
            ("Agent identity pilots in enterprise stacks", "technology", "Agent Identity"),
            ("Machine-payable API experiments", "market", "Agent Commerce"),
            ("Stablecoin rails for micropayments", "business", "Stablecoins"),
            ("Computer-use agents operating procurement portals", "developer", "Computer Use"),
        ]
        signal_ids = []
        for title, category, tech in signal_rows:
            sid = new_id("sig")
            signal_ids.append(sid)
            db.add(
                Signal(
                    id=sid,
                    title=title,
                    category=category,
                    source="FutureLab Demo Seed",
                    source_url="",
                    summary="Labeled demo signal — not a factual external claim.",
                    evidence=["demo-seed"],
                    novelty_score=7.2,
                    momentum_score=7.8,
                    confidence=0.55,
                    tags=["demo"],
                    claim_type="INFERENCE",
                    technologies=[tech],
                    run_id=run.id,
                    is_demo=True,
                )
            )

        conv_id = new_id("cvg")
        db.add(
            Convergence(
                id=conv_id,
                title="Agent Identity × Stablecoins × Authorization",
                thesis="Autonomous commerce needs identity, policy, and settlement at once.",
                nodes=["Agent Identity", "Stablecoins", "Authorization"],
                why_connect="Signals cluster around agents that can act and pay, but cannot yet trust each other.",
                consequences=["Escrow becomes necessary", "Reputation may precede credit"],
                opportunities=["Agent Escrow", "Machine Reputation Network"],
                signal_ids=signal_ids,
                strength=8.7,
                run_id=run.id,
                is_demo=True,
            )
        )

        demo_ideas = [
            {
                "name": "Agent Escrow",
                "one_liner": "A programmable transaction and trust layer for autonomous AI-to-AI commerce.",
                "score": 89,
                "band": "prototype_candidate",
                "status": "winner",
                "winner": True,
                "why_now": "Agent identity + autonomous purchasing + machine payments are converging.",
            },
            {
                "name": "Ambient Memory Layer",
                "one_liner": "A continuous memory substrate for humans and agents.",
                "score": 84,
                "band": "prototype_candidate",
                "status": "watch",
            },
            {
                "name": "AI Legacy App Operator",
                "one_liner": "An operator that uses existing enterprise GUIs instead of waiting for APIs.",
                "score": 82,
                "band": "prototype_candidate",
                "status": "watch",
            },
            {
                "name": "Machine Reputation Network",
                "one_liner": "Portable reputation for non-human actors across tools and vendors.",
                "score": 67,
                "band": "interesting",
                "status": "resurrected",
                "resurrected": True,
                "original_score": 67,
            },
            {
                "name": "Personal World Model",
                "one_liner": "A private, continuously updated model of a person's work and commitments.",
                "score": 81,
                "band": "prototype_candidate",
                "status": "watch",
            },
            {
                "name": "Autonomous Procurement Agent",
                "one_liner": "An agent that buys routine inputs under policy, with escrow and audit built in.",
                "score": 78,
                "band": "watch",
                "status": "watch",
            },
        ]

        winner_id = None
        for spec in demo_ideas:
            iid = new_id("idea")
            if spec.get("winner"):
                winner_id = iid
            db.add(
                Idea(
                    id=iid,
                    slug=spec["name"].lower().replace(" ", "-"),
                    name=spec["name"],
                    one_liner=spec["one_liner"],
                    problem="Demo problem statement.",
                    customer="Demo customer persona.",
                    future_thesis="Demo future thesis.",
                    technology_convergence=["Agent Identity", "Stablecoins"],
                    why_now=spec.get("why_now", "Why-now thesis for demo."),
                    why_difficult_before="Previously missing substrate.",
                    what_recently_changed="Recent capability convergence.",
                    current_alternatives=["Incumbent workaround"],
                    novelty="Demo novelty thesis.",
                    potential_moat="Data + attestation graph.",
                    mvp="Smallest useful version for demo.",
                    architecture="Local-first service with policy engine and audit log.",
                    risks=["Incumbent checkbox feature"],
                    unknowns=["Adoption timing"],
                    why_may_win="Strong why-now.",
                    why_may_fail="Market may be early.",
                    market="Infrastructure",
                    first_customer="Agent marketplace operator",
                    product=spec["one_liner"],
                    mode="missing-primitive",
                    status=spec["status"],
                    score=spec["score"],
                    score_band=spec["band"],
                    confidence=0.84,
                    original_score=spec.get("original_score"),
                    resurrected=spec.get("resurrected", False),
                    run_id=run.id,
                    signal_ids=signal_ids,
                    convergence_id=conv_id,
                    is_demo=True,
                    is_winner=spec.get("winner", False),
                    fingerprint=spec["name"],
                )
            )
            db.add(
                IdeaScore(
                    id=new_id("scr"),
                    idea_id=iid,
                    run_id=run.id,
                    dimensions={"novelty": {"score": 8.8, "reason": "demo", "evidence": [], "confidence": 0.8}},
                    weighted_total=spec["score"],
                    band=spec["band"],
                    reason="Demo scorecard",
                    evidence=["demo-seed"],
                    confidence=0.84,
                )
            )
            if spec["name"] == "Agent Escrow":
                db.add(
                    AgentEvaluation(
                        id=new_id("eval"),
                        idea_id=iid,
                        run_id=run.id,
                        role="futurist",
                        stance="for",
                        quote="This category becomes necessary if agent commerce scales.",
                        full_text="Second-order effects favor a neutral hold primitive.",
                        confidence=0.8,
                    )
                )
                db.add(
                    AgentEvaluation(
                        id=new_id("eval"),
                        idea_id=iid,
                        run_id=run.id,
                        role="skeptic",
                        stance="against",
                        quote="Payment providers could add this themselves.",
                        full_text="Incumbent risk is real but timing may beat them.",
                        confidence=0.72,
                    )
                )
                db.add(
                    Prototype(
                        id=new_id("proto"),
                        idea_id=iid,
                        run_id=run.id,
                        name="Agent Escrow",
                        status="built",
                        stack=["html", "css", "vanilla-js"],
                        local_path="outputs/futurelab/demo/prototype",
                        launch_command="open outputs/futurelab/demo/prototype/index.html",
                        architecture="Policy engine + escrow state machine + audit log.",
                        readme="Demo prototype placeholder.",
                        tests_passed=True,
                        is_demo=True,
                    )
                )

        run.winner_id = winner_id
        db.add(
            MemoryItem(
                id=new_id("mem"),
                learning="Pure chatbot concepts rarely survive final review.",
                evidence=["obvious-filter", "novelty cap"],
                category="pattern",
                is_demo=True,
            )
        )
        db.add(
            MemoryItem(
                id=new_id("mem"),
                learning="Agent identity appears in 14 high-scoring future scenarios.",
                evidence=["demo-seed", "convergence map"],
                category="pattern",
                is_demo=True,
            )
        )

        timeline = [
            ("10:31 PM", "Signal discovery started"),
            ("10:58 PM", "317 signals processed"),
            ("11:21 PM", "11 unusual convergences detected"),
            ("11:44 PM", "100 candidate inventions generated"),
            ("12:08 AM", "76 rejected"),
            ("12:44 AM", "5 finalists selected"),
            ("1:17 AM", "Agent debate completed"),
            ("1:35 AM", "Winner selected"),
            ("1:56 AM", "Architecture generated"),
            ("2:14 AM", "Prototype started"),
            ("3:03 AM", "Tests passed"),
            ("3:19 AM", "Prototype complete"),
        ]
        base = now - timedelta(hours=5)
        for idx, (stamp, message) in enumerate(timeline):
            db.add(
                TimelineEvent(
                    id=new_id("evt"),
                    run_id=run.id,
                    occurred_at=base + timedelta(minutes=idx * 18),
                    stage="timeline",
                    message=f"{stamp} — {message}",
                )
            )

        if winner_id:
            db.add(
                IdeaHistory(
                    id=new_id("hst"),
                    idea_id=winner_id,
                    event="won",
                    payload={"run": run.id, "score": 89},
                )
            )

        db.commit()
    finally:
        db.close()
