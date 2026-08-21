from app.builder.readme import render_fancy_readme
from app.database.models import Idea
from app.scoring.domain import enforce_ai_theme, is_ai_agentic_scope


def test_agent_escrow_in_scope():
    ok, reason = is_ai_agentic_scope(
        name="Agent Escrow",
        one_liner="A programmable trust layer for autonomous AI-to-AI commerce.",
        problem="Agents can initiate purchases without a hold primitive.",
        product="Programmable escrow for autonomous counterparties.",
        technology_convergence=["Agent Identity", "Stablecoins"],
    )
    assert ok, reason


def test_non_ai_rejected():
    ok, reason = is_ai_agentic_scope(
        name="Neighborhood Compost Exchange",
        one_liner="Match households with leftover produce for composting.",
        problem="Food waste in suburbs.",
        product="A local marketplace for compost.",
    )
    assert not ok
    assert "Out of scope" in reason


def test_generic_ai_wrapper_rejected():
    ok, reason = is_ai_agentic_scope(
        name="Smart Notes",
        one_liner="An AI writing assistant for meeting notes.",
        problem="People forget meeting details.",
        product="Notes app with summarization.",
    )
    assert not ok


def test_enforce_ai_theme():
    assert enforce_ai_theme("") == "Autonomous AI Agents"
    assert enforce_ai_theme("Autonomous AI Agents") == "Autonomous AI Agents"
    assert enforce_ai_theme("Coffee shops") == "Autonomous AI Agents"


def test_fancy_readme_has_sections():
    idea = Idea(
        id="idea_test",
        slug="agent-escrow",
        name="Agent Escrow",
        one_liner="Trust layer for autonomous AI agents.",
        problem="No hold primitive for agent commerce.",
        customer="Agent marketplaces",
        future_thesis="Agents need escrow before banks.",
        technology_convergence=["Agent Identity", "Stablecoins"],
        why_now="Machine-payable APIs are arriving.",
        why_difficult_before="Agents could not act reliably.",
        what_recently_changed="Tool-calling agents.",
        current_alternatives=["Stripe Connect"],
        novelty="Agent-native escrow.",
        potential_moat="Condition DSL",
        mvp="Create escrow and release on evidence.",
        architecture="Intent API → predicate engine → custody",
        risks=["Regulation"],
        unknowns=["Volume timing"],
        why_may_win="Commerce needs a hold primitive.",
        why_may_fail="Incumbents ship a checkbox.",
        market="Machine commerce",
        first_customer="An agent marketplace",
        product="Programmable escrow",
        mode="missing-primitive",
        status="winner",
    )
    md = render_fancy_readme(idea, local_path="/tmp/proto", github_url="https://github.com/acme/futurelab-agent-escrow")
    assert "# Agent Escrow" in md
    assert "Why this exists" in md
    assert "Architecture" in md
    assert "AI + Agentic" in md or "AI and Agentic" in md
    assert "https://github.com/acme/futurelab-agent-escrow" in md
    assert "![AI]" in md
