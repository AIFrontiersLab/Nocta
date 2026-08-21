from __future__ import annotations

from app.database.models import Idea


def render_fancy_readme(idea: Idea, *, local_path: str = "", github_url: str = "") -> str:
    """Polished README for AI / Agentic prototype repos."""
    tags = [
        "ai",
        "agentic-ai",
        "autonomous-agents",
        "vectra-futurelab",
        "prototype",
    ]
    conv = idea.technology_convergence or []
    if isinstance(conv, list):
        for item in conv[:4]:
            slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(item)).strip("-")
            if slug:
                tags.append(slug[:32])

    badge_ai = "![AI](https://img.shields.io/badge/domain-AI%20%2B%20Agentic-0ea5e9?style=for-the-badge)"
    badge_lab = "![FutureLab](https://img.shields.io/badge/built%20by-Vectra%20FutureLab-111827?style=for-the-badge)"
    badge_status = "![Status](https://img.shields.io/badge/status-isolated%20prototype-22c55e?style=for-the-badge)"

    risks = idea.risks or []
    unknowns = idea.unknowns or []
    alternatives = idea.current_alternatives or []
    assumptions = []
    if getattr(idea, "assumptions", None):
        assumptions = [a.statement for a in idea.assumptions if getattr(a, "statement", None)]

    risk_lines = "\n".join(f"- {r}" for r in risks) or "- TBD during pilot"
    unknown_lines = "\n".join(f"- {u}" for u in unknowns) or "- Adoption timing"
    alt_lines = "\n".join(f"- {a}" for a in alternatives) or "- Manual ops / incumbent tooling"
    assumption_lines = "\n".join(f"- {a}" for a in assumptions) or "- Agent workflows will keep expanding into real systems"
    conv_lines = ", ".join(str(c) for c in conv) if conv else "Agent runtimes, tool calling, trusted execution"

    repo_line = f"**Repository:** [{github_url}]({github_url})" if github_url else "**Repository:** local prototype (not published)"
    launch = (
        f'```bash\npython3 -m http.server 4173 --directory "{local_path}"\n```'
        if local_path
        else "Open `index.html` in a browser."
    )

    return f"""# {idea.name}

{badge_ai} {badge_lab} {badge_status}

> {idea.one_liner}

{repo_line}

---

## Why this exists

{idea.problem}

**Why now:** {idea.why_now}

**What recently changed:** {idea.what_recently_changed or "Agent capability + distribution crossed a useful threshold."}

**Why it was hard before:** {idea.why_difficult_before or "Agents lacked durable identity, permissions, and reliable tool loops."}

---

## Product thesis

| | |
|---|---|
| **Future thesis** | {idea.future_thesis or "Agentic systems need missing infrastructure primitives."} |
| **First customer** | {idea.first_customer or idea.customer} |
| **Market** | {idea.market or "Agentic AI infrastructure"} |
| **Convergence** | {conv_lines} |
| **Moat** | {idea.potential_moat or "Execution quality + workflow depth"} |

---

## MVP

{idea.mvp}

### Core loop

1. Accept an agent (or human-on-behalf-of-agent) intent
2. Enforce scope / policy / evidence
3. Execute the smallest useful autonomous step
4. Leave an audit trail a human can kill-switch

---

## Architecture

```text
{idea.architecture or "Intent API → policy/runtime → tools → audit log"}
```

---

## Quick start

{launch}

---

## Why it may win

{idea.why_may_win or "It removes a blocker that demos hit before production."}

## Why it may fail

{idea.why_may_fail or "Incumbents ship a checkbox feature."}

### Risks

{risk_lines}

### Unknowns

{unknown_lines}

### Current alternatives

{alt_lines}

### Assumptions

{assumption_lines}

---

## Scope

This project is intentionally scoped to **AI and Agentic AI** only.

---

## Tags

{" ".join(f"`{t}`" for t in tags)}
"""
