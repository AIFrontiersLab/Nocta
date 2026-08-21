from __future__ import annotations

from pathlib import Path

from app.database.models import Idea, Prototype, Run


def _normalize_prototypes(
    prototype: Prototype | None | list[Prototype],
) -> list[Prototype]:
    if prototype is None:
        return []
    if isinstance(prototype, list):
        return [p for p in prototype if p is not None]
    return [prototype]


def morning_report_markdown(
    run: Run,
    winner: Idea | None,
    prototype: Prototype | None | list[Prototype],
) -> str:
    name = winner.name if winner else "No winner"
    one = winner.one_liner if winner else ""
    thesis = winner.future_thesis if winner else ""
    why = winner.why_now if winner else ""
    collision = "\n+".join(winner.technology_convergence or []) if winner else ""
    customer = (winner.first_customer or winner.customer) if winner else ""
    market = winner.market if winner else ""
    mvp = winner.mvp if winner else ""
    prototypes = _normalize_prototypes(prototype)
    if not prototypes:
        proto_block = "NOT BUILT\n\nPath: "
    else:
        lines: list[str] = []
        for idx, proto in enumerate(prototypes, start=1):
            state = (proto.status or "built").upper()
            path = proto.local_path or ""
            gh = f"\nGitHub: {proto.github_url}" if proto.github_url else ""
            lines.append(f"{idx}. **{proto.name}** — {state}\nPath: {path}{gh}")
        proto_block = "\n\n".join(lines)
    score = f"{winner.score:.0f} / 100" if winner else "—"
    rec = run.recommendation or "WATCH"
    return f"""# VECTRA FUTURELAB — MORNING REPORT

## Last Night's Invention

**{name}**

{one}

## Future Thesis

{thesis}

## Why Now

{why}

## Technology Collision

{collision}

## First Customer

{customer}

## Business Potential

{market}

## MVP

{mvp}

## Agent Debate

See the dashboard for the full boardroom. Strongest arguments are stored with the idea.

## FutureLab Score

{score}

## Prototypes ({len(prototypes)} built / published)

{proto_block}

## Interesting Discovery

{run.unexpected_insight}

## Recommendation

{rec}

---
Run `{run.id}` · mode `{run.mode}` · {run.signals_count} signals · {run.ideas_generated} ideas generated · {run.ideas_rejected} rejected
"""


def whatsapp_payload(
    run: Run,
    winner: Idea | None,
    prototype: Prototype | None | list[Prototype],
) -> str:
    name = winner.name if winner else "No winner"
    one = winner.one_liner if winner else run.hypothesis
    prototypes = _normalize_prototypes(prototype)
    published = [p for p in prototypes if p.github_url]
    if published:
        proto = f"✅ {len(prototypes)} built · {len(published)} GitHub repo(s)"
        for p in published:
            proto += f"\n- {p.name}: {p.github_url}"
    elif prototypes:
        proto = f"✅ {len(prototypes)} built (local)"
    else:
        proto = "Not built"
    score = f"{winner.score:.0f}/100" if winner else "—"
    return f"""🚀 VECTRA FUTURELAB

Last night I explored:
{run.theme or run.hypothesis}

Experiment:
{run.mode}

Winner:
{name}

Concept:
{one}

FutureLab Score:
{score}

Prototypes:
{proto}

Unexpected insight:
{run.unexpected_insight or 'See morning report.'}

Recommendation:
{run.recommendation or 'Worth reviewing today.'}
"""


def write_run_artifacts(output_dir: Path, markdown: str, payload: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report").mkdir(exist_ok=True)
    (output_dir / "report" / "morning-report.md").write_text(markdown, encoding="utf-8")
    (output_dir / "report" / "whatsapp.txt").write_text(payload, encoding="utf-8")
