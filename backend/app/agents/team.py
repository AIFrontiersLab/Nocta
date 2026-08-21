from __future__ import annotations

from app.llm.router import ModelRouter
from app.llm.schemas import AgentTake, DimensionBundle, IdeaDraft, JudgeDecision
from app.llm.prompt_loader import load_prompt
from app.utils.logging import get_logger

log = get_logger("agents")

ROLES = [
    "futurist",
    "inventor",
    "entrepreneur",
    "product_designer",
    "engineer",
    "investor",
    "skeptic",
    "historian",
    "contrarian",
    "customer_simulator",
    "judge",
]


def _idea_blob(idea: IdeaDraft) -> str:
    return (
        f"Name: {idea.name}\nOne-liner: {idea.one_liner}\nProblem: {idea.problem}\n"
        f"Customer: {idea.customer}\nWhy now: {idea.why_now}\nMVP: {idea.mvp}\n"
        f"Risks: {idea.risks}\nThesis: {idea.future_thesis}"
    )


def heuristic_take(role: str, idea: IdeaDraft) -> AgentTake:
    name = idea.name
    table = {
        "futurist": AgentTake(
            role="futurist",
            stance="for",
            quote=f"If {name} is 10× larger, adjacent markets reorganize around it.",
            full_text=f"Second-order: {idea.future_thesis or idea.one_liner}",
            confidence=0.62,
            score_hint=8.0,
        ),
        "inventor": AgentTake(
            role="inventor",
            stance="for",
            quote=f"{name} is a new object, not a feature on an old object.",
            full_text=idea.novelty or idea.one_liner,
            confidence=0.6,
            score_hint=8.2,
        ),
        "entrepreneur": AgentTake(
            role="entrepreneur",
            stance="mixed",
            quote=f"First payer is {idea.first_customer or idea.customer}.",
            full_text=f"Monetization depends on whether {idea.customer} already feels acute pain.",
            confidence=0.58,
            score_hint=7.2,
        ),
        "product_designer": AgentTake(
            role="product_designer",
            stance="mixed",
            quote="Someone will want this if the first job is painfully specific.",
            full_text=f"MVP: {idea.mvp}",
            confidence=0.6,
            score_hint=7.0,
        ),
        "engineer": AgentTake(
            role="engineer",
            stance="for" if idea.architecture else "mixed",
            quote="An MVP is technically feasible today with existing models and rails.",
            full_text=idea.architecture or "Feasible as a local-first service with human approval gates.",
            confidence=0.66,
            score_hint=7.8,
        ),
        "investor": AgentTake(
            role="investor",
            stance="mixed",
            quote="Large upside, but adoption timing is the entire risk.",
            full_text=idea.market or idea.why_now,
            confidence=0.55,
            score_hint=7.1,
        ),
        "skeptic": AgentTake(
            role="skeptic",
            stance="destroy",
            quote=idea.why_may_fail or "An incumbent can ship a checkbox version.",
            full_text="; ".join(idea.risks) if idea.risks else idea.why_may_fail,
            confidence=0.7,
            score_hint=4.8,
        ),
        "historian": AgentTake(
            role="historian",
            stance="mixed",
            quote="Comparable trust layers emerged after previous platform shifts — usually late.",
            full_text=idea.why_difficult_before or "Prior cycles failed when the substrate was missing.",
            confidence=0.64,
            score_hint=6.8,
        ),
        "contrarian": AgentTake(
            role="contrarian",
            stance="mixed",
            quote="The popular belief (payments first) may be wrong; reputation or identity may precede money.",
            full_text="Question the sequencing everyone treats as obvious.",
            confidence=0.6,
            score_hint=7.4,
        ),
        "customer_simulator": AgentTake(
            role="customer_simulator",
            stance="mixed",
            quote=f"[SIMULATED] {idea.customer} would trial this if onboarding is under a day.",
            full_text="Simulated reaction only — not genuine customer validation.",
            confidence=0.4,
            score_hint=6.5,
        ),
    }
    return table.get(
        role,
        AgentTake(role=role, stance="mixed", quote="No view.", full_text="", confidence=0.4),
    )


def run_agent(role: str, idea: IdeaDraft, llm: ModelRouter | None) -> AgentTake:
    if llm is None or role == "judge":
        return heuristic_take(role, idea)
    try:
        system = load_prompt(f"agents/{role}")
        user = _idea_blob(idea) + "\nReturn JSON with keys role, stance, quote, full_text, confidence, score_hint."
        take = llm.complete_model(system, user, AgentTake, tier="reasoning")
        take.role = role
        return take
    except Exception as exc:
        log.warning(f"agent {role} fell back: {exc}")
        return heuristic_take(role, idea)


def debate_idea(idea: IdeaDraft, llm: ModelRouter | None, *, roles: list[str] | None = None) -> list[AgentTake]:
    selected = roles or [r for r in ROLES if r != "judge"]
    takes = []
    for role in selected:
        takes.append(run_agent(role, idea, llm))
    return takes


def judge_finalists(
    ideas: list[IdeaDraft],
    debates: dict[str, list[AgentTake]],
    scores: dict[str, float],
    llm: ModelRouter | None,
) -> JudgeDecision:
    if not ideas:
        return JudgeDecision(winner_name="", decision="ARCHIVE", confidence=0.2, reasoning="No ideas")
    ranked = sorted(ideas, key=lambda i: scores.get(i.name, 0), reverse=True)
    default_winner = ranked[0]
    if llm is None:
        return JudgeDecision(
            winner_name=default_winner.name,
            finalists=[i.name for i in ranked[:5]],
            decision="PROTOTYPE" if scores.get(default_winner.name, 0) >= 80 else "WATCH",
            confidence=0.72,
            reasoning="Judge used transparent scores; consensus was not required.",
            dissent="Skeptic arguments were retained rather than averaged away.",
            unexpected_insight="The strongest idea may be the one skeptics called 'too early' if why-now evidence is new.",
        )
    try:
        system = load_prompt("agents/judge")
        payload = []
        for idea in ranked[:5]:
            payload.append(
                {
                    "name": idea.name,
                    "score": scores.get(idea.name),
                    "debate": [t.model_dump() for t in debates.get(idea.name, [])],
                }
            )
        user = (
            "Select a winner. Do NOT automatically pick the consensus favorite. "
            "You may pick a polarizing idea if evidence is stronger.\n"
            f"{payload}\nReturn JSON JudgeDecision."
        )
        decision = llm.complete_model(system, user, JudgeDecision, tier="reasoning")
        names = {i.name for i in ideas}
        if decision.winner_name not in names:
            decision.winner_name = default_winner.name
        return decision
    except Exception as exc:
        log.warning(f"judge fell back: {exc}")
        return JudgeDecision(
            winner_name=default_winner.name,
            finalists=[i.name for i in ranked[:5]],
            decision="WATCH",
            confidence=0.6,
            reasoning=f"Judge fallback after error: {exc}",
        )


def score_dimensions_for_idea(
    idea: IdeaDraft,
    *,
    signal_confidence: float,
    novelty_bonus: float,
    llm: ModelRouter | None,
) -> DimensionBundle:
    """LLMs may propose dimension scores; the weighted total is computed later in code."""
    if llm is not None:
        try:
            system = load_prompt("agents/scorer")
            user = _idea_blob(idea) + "\nReturn JSON {dimensions: {name: {score, reason, evidence, confidence}}}"
            bundle = llm.complete_model(system, user, DimensionBundle, tier="reasoning")
            return bundle
        except Exception as exc:
            log.warning(f"scorer fell back: {exc}")

    def dim(score: float, reason: str, conf: float = 0.55) -> dict:
        return {"score": max(0, min(10, score)), "reason": reason, "evidence": [reason], "confidence": conf}

    why_now = 7.4 + novelty_bonus
    return DimensionBundle.model_validate(
        {
            "dimensions": {
                "novelty": dim(7.6 + novelty_bonus, idea.novelty or "Unusual combination"),
                "problem_severity": dim(7.8, idea.problem[:180]),
                "market_potential": dim(7.1, idea.market or "Emerging infrastructure"),
                "why_now": dim(why_now, idea.why_now or "Timing thesis present"),
                "technical_feasibility": dim(7.5, "MVP can be built with current models and rails"),
                "competitive_white_space": dim(7.4, "Category is unnamed or weakly owned"),
                "defensibility": dim(6.8, idea.potential_moat or "Data/attestation network effects possible"),
                "distribution_potential": dim(6.4, "Likely bottoms-up through agent platforms"),
                "revenue_potential": dim(7.0, "Infrastructure can charge take-rate or seats"),
                "wow_factor": dim(7.7, idea.one_liner),
                "prototypeability": dim(8.2, idea.mvp[:180] or "Narrow MVP exists"),
                "signal_confidence": dim(signal_confidence, "Derived from collected signals, not vibes"),
            }
        }
    )
