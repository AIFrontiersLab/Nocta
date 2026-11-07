from __future__ import annotations

import re

from app.database.models import Idea


def _mermaid_escape(text: str) -> str:
    """Keep Mermaid node labels readable and safe."""
    cleaned = re.sub(r"[\"\[\]]", "", (text or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:48] or "Step"


def _architecture_mermaid(architecture: str, product_name: str) -> str:
    """Build a flowchart from arrow-separated architecture text, with a sensible default."""
    raw = (architecture or "").strip()
    parts = [p.strip(" .") for p in re.split(r"\s*(?:→|->|—>|=>|/|;|,)\s*", raw) if p.strip(" .")]
    # Prefer short stage names; long prose becomes a single summary node
    if len(parts) < 2 or any(len(p) > 40 for p in parts):
        parts = [
            "Intent / capture",
            "Policy & clustering",
            "Proposal UI",
            "Operator / audit",
        ]

    nodes: list[str] = []
    edges: list[str] = []
    for idx, part in enumerate(parts[:6]):
        key = chr(ord("A") + idx)
        nodes.append(f'  {key}["{_mermaid_escape(part)}"]')
        if idx > 0:
            prev = chr(ord("A") + idx - 1)
            edges.append(f"  {prev} --> {key}")

    label = _mermaid_escape(product_name)
    return (
        "```mermaid\n"
        "flowchart LR\n"
        f'  subgraph Product["{label}"]\n'
        + "\n".join(nodes)
        + "\n  end\n"
        + "\n".join(edges)
        + "\n```"
    )


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

    arch_text = idea.architecture or "Intent API → policy/runtime → tools → audit log"
    arch_mermaid = _architecture_mermaid(arch_text, idea.name or "Prototype")

    repo_line = f"**Repository:** [{github_url}]({github_url})" if github_url else "**Repository:** local prototype (not published)"
    # README lives inside the prototype dir — use relative path so GitHub clones work.
    launch = (
        "```bash\npython3 -m http.server 4173 --directory .\n```"
        if local_path or github_url
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
{arch_text}
```

{arch_mermaid}

---

## Start

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
