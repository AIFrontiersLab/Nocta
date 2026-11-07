# Nocta

**Invent Tomorrow While You Sleep.**

Nocta is a local-first autonomous innovation laboratory. Every night it can explore weak signals, detect convergences, generate and reject many ideas, debate them with role-specific agents, score opportunities transparently, optionally build an isolated prototype, and present a morning experience:

> **While you were sleeping, Nocta invented this.**

## What it is

- Autonomous R&D lab + invention studio + future simulator
- Not an AI news dashboard or generic idea generator
- SQLite-backed memory, resurrection engine, convergence map, and polished dashboard

## Quick start

```bash
cd /path/to/Nocta   # this repo
cp .env.example .env

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m app.cli seed
PYTHONPATH=. python -m app.cli run --mode missing-primitive --theme "Autonomous AI Agents" --build
PYTHONPATH=. python -m app.cli serve

# Frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

Open **http://127.0.0.1:3000**

API health: **http://127.0.0.1:8787/api/health**

## Hermes nightly job

```bash
chmod +x scripts/nocta-nightly.sh
./scripts/install_hermes.sh
```

Suggested schedule: `30 22 * * *` (10:30 PM). The installer creates a Hermes wrapper at `~/.hermes/scripts/nocta-nightly.sh` without modifying unrelated cron jobs.

The nightly script runs with `--build` and creates up to **`DAILY_PROTOTYPE_COUNT`** prototypes (default **2**). With `GITHUB_AUTO_PUBLISH=true`, that means **2 new GitHub repos per day** (winner + next finalist).

Manual run:

```bash
./scripts/nocta-nightly.sh
# or
nocta run --mode auto
```

## CLI

```bash
cd backend
PYTHONPATH=. python -m app.cli run --mode auto
PYTHONPATH=. python -m app.cli run --mode missing-primitive
PYTHONPATH=. python -m app.cli run --mode technology-collision
PYTHONPATH=. python -m app.cli seed
PYTHONPATH=. python -m app.cli serve
```

## Architecture

```text
nocta/
├── backend/            FastAPI + SQLAlchemy + orchestrator
│   ├── analytics/      Run metrics, cost tracker, trends
│   ├── evaluation/     Filter/eval harness + baselines
│   ├── research/       Signal adapters (HN, GitHub, papers)
│   └── ...
├── frontend/           Next.js dashboard + analytics UI
├── docs/               Architecture / API / modes
├── scripts/            Hermes wrappers
├── outputs/nocta/  Per-run artifacts
├── data/               SQLite database
└── tests/
```

See also `docs/ARCHITECTURE.md`, `docs/API.md`, and `CONTRIBUTING.md`.

### Core pipeline

```text
signals → convergences → mode selection → idea generation
→ filters → scoring → agent debate → judge → prototype → morning report
→ analytics / evaluation
```

### Reused infrastructure

- **Hermes** cron + script wrapper pattern (same as FutureTech / IdeaDestruction)
- **WhatsApp** via existing `hermes send` (`MorningNotifier`)
- **SharedRoute** at `http://10.0.0.27:8088/v1` (`model=router`, task via `X-Route-Task`)
- **Signal adapters** inspired by InnovationScanner (HN, GitHub, papers)

## Environment

See `.env.example` for:

- SharedRoute (`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `AI_MODEL`, `AI_PROJECT`)
- cost limits (`MAX_MODEL_CALLS`, `MAX_RUNTIME_MINUTES`, `PROTOTYPE_THRESHOLD`)
- domain scope (`REQUIRE_AI_AGENTIC_SCOPE`, `DEFAULT_THEME`)
- GitHub publish (`GITHUB_AUTO_PUBLISH`, `GITHUB_OWNER`, `GITHUB_TOKEN`, `GITHUB_PRIVATE`)
- Hermes/WhatsApp (`HERMES_ENABLED`, `HERMES_WHATSAPP_GROUP`, `NOCTA_SEND_WHATSAPP`)

### LLM routing

All completions go through SharedRoute. The app never talks to Ollama hosts or individual oMLX machines.

```text
Nocta
       ↓
OPENAI_BASE_URL + model=router
X-Route-Project / X-Route-Task
       ↓
http://10.0.0.27:8088/v1
       ↓
SharedRoute → FAST / MEDIUM / HEAVY → oMLX backends
```

Typical Nocta tasks (most core work → **HEAVY** via task name):

| Workload | `X-Route-Task` |
|---|---|
| Idea feasibility / agent debate / scoring | `complex_reasoning` |
| Final judge decision | `deep_analysis` |
| Market / technology research | `deep_research` |
| Architecture decisions | `architecture` |
| Code scaffolding | `code_generation` |
| Code review / debug | `code_review` / `debugging` |
| Multi-step project planning | `agent_planning` |
| README / announcements | `content_generation` |
| Classification / short metadata | `classification` / `simple_summary` |

## Safety

Nocta may research, reason, write local artifacts, and build isolated prototypes.

By default it will **not** email, purchase, deploy publicly, or modify unrelated repositories.

**Domain scope:** when `REQUIRE_AI_AGENTIC_SCOPE=true` (default), every candidate must be **AI + Agentic AI**. Non-agentic ideas are rejected.

**GitHub publish (opt-in):** set `GITHUB_AUTO_PUBLISH=true`, `GITHUB_TOKEN`, and `GITHUB_OWNER`. Then each built prototype creates a **new** repo, commits a fancy README + demo, and pushes — only inside that isolated prototype directory. Repos default to **public** (`GITHUB_PRIVATE=false`). Set `GITHUB_PRIVATE=true` only if you want private repos. Set `DAILY_PROTOTYPE_COUNT=2` (default) so a nightly `--build` run publishes **two** repos.

Prototype builds still require `--build` when `REQUIRE_HUMAN_APPROVAL_FOR_BUILD=true`.

## Tests

```bash
cd backend
source .venv/bin/activate
pytest ../tests -q
```

## Demo data

`python -m app.cli seed` loads labeled demo content (Agent Escrow hero, convergence map, timeline). Demo rows are marked `is_demo=true` and do not fabricate external news.

## Troubleshooting

- **Empty dashboard**: run `seed` or start a run via Experiments screen
- **LLM unavailable**: checks SharedRoute at `OPENAI_BASE_URL` (`http://10.0.0.27:8088/v1`); otherwise continues with catalog + heuristic scoring
- **WhatsApp not sent**: set `HERMES_ENABLED=true`, `NOCTA_SEND_WHATSAPP=true`, and `HERMES_WHATSAPP_GROUP`
