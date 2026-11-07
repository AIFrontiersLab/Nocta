# Architecture

Nocta is a local-first overnight invention lab.

## Layers

1. **Research** — signal adapters (GitHub, HN, papers) + convergence detection
2. **Modes** — missing-primitive, technology-collision, resurrection, auto
3. **Generation & filters** — idea drafts, obvious/impossible filters, domain scope
4. **Scoring & debate** — weighted scorecard + multi-agent critique
5. **Judgment & build** — winner selection, optional isolated prototype
6. **Delivery** — morning report, dashboard, optional WhatsApp via Hermes
7. **Memory** — SQLite history, learnings, resurrection candidates
8. **Analytics** — run metrics, cost estimates, evaluation harness

## Runtime topology

```text
CLI / Hermes cron
    → orchestration.pipeline.run_experiment
        → research → modes → scoring → agents → builder → reporter
    → FastAPI (dashboard + analytics)
    → Next.js UI
```

## LLM path

All completions go through SharedRoute (`OPENAI_BASE_URL`, `model=router`) with task headers. The app does not talk to individual model hosts directly.
