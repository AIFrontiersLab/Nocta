# Vectra FutureLab

**Invent Tomorrow While You Sleep.**

Vectra FutureLab is a local-first autonomous innovation laboratory. Every night it can explore weak signals, detect convergences, generate and reject many ideas, debate them with role-specific agents, score opportunities transparently, optionally build an isolated prototype, and present a morning experience:

> **While you were sleeping, FutureLab invented this.**

## What it is

- Autonomous R&D lab + invention studio + future simulator
- Not an AI news dashboard or generic idea generator
- SQLite-backed memory, resurrection engine, convergence map, and polished dashboard

## Quick start

```bash
cd /Users/aiserver/Workspace_New/VectraFutureLab
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
chmod +x scripts/futurelab-nightly.sh
./scripts/install_hermes.sh
```

Suggested schedule: `30 22 * * *` (10:30 PM). The installer creates a Hermes wrapper at `~/.hermes/scripts/futurelab-nightly.sh` without modifying unrelated cron jobs.

The nightly script runs with `--build` and creates up to **`DAILY_PROTOTYPE_COUNT`** prototypes (default **2**). With `GITHUB_AUTO_PUBLISH=true`, that means **2 new GitHub repos per day** (winner + next finalist).

Manual run:

```bash
./scripts/futurelab-nightly.sh
# or
futurelab run --mode auto
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
futurelab/
├── backend/          FastAPI + SQLAlchemy + orchestrator
├── frontend/           Next.js dashboard
├── scripts/            Hermes wrappers
├── outputs/futurelab/  Per-run artifacts
├── data/               SQLite database
└── tests/
```

### Core pipeline

```text
signals → convergences → mode selection → idea generation
→ filters → scoring → agent debate → judge → prototype → morning report
```

### Reused infrastructure

- **Hermes** cron + script wrapper pattern (same as FutureTech / IdeaDestruction)
- **WhatsApp** via existing `hermes send` (`MorningNotifier`)
- **Ollama/OpenAI** model router pattern from sibling labs
- **Signal adapters** inspired by InnovationScanner (HN, GitHub, papers)

## Environment

See `.env.example` for:

- model routing (`LLM_*` vars — no hardcoded model names in code)
- cost limits (`MAX_MODEL_CALLS`, `MAX_RUNTIME_MINUTES`, `PROTOTYPE_THRESHOLD`)
- domain scope (`REQUIRE_AI_AGENTIC_SCOPE`, `DEFAULT_THEME`)
- GitHub publish (`GITHUB_AUTO_PUBLISH`, `GITHUB_OWNER`, `GITHUB_TOKEN`, `GITHUB_PRIVATE`)
- Hermes/WhatsApp (`HERMES_ENABLED`, `HERMES_WHATSAPP_GROUP`, `FUTURELAB_SEND_WHATSAPP`)

## Safety

FutureLab may research, reason, write local artifacts, and build isolated prototypes.

By default it will **not** email, purchase, deploy publicly, or modify unrelated repositories.

**Domain scope:** when `REQUIRE_AI_AGENTIC_SCOPE=true` (default), every candidate must be **AI + Agentic AI**. Non-agentic ideas are rejected.

**GitHub publish (opt-in):** set `GITHUB_AUTO_PUBLISH=true`, `GITHUB_TOKEN`, and `GITHUB_OWNER`. Then each built prototype creates a **new** repo, commits a fancy README + demo, and pushes — only inside that isolated prototype directory. Repos default to **private** (`GITHUB_PRIVATE=true`). Set `DAILY_PROTOTYPE_COUNT=2` (default) so a nightly `--build` run publishes **two** repos.

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
- **LLM unavailable**: tries `OLLAMA_HOST` (`http://10.0.0.25:11434`), then falls back to `OLLAMA_FALLBACK_HOST` (`http://localhost:11434`) with **`OLLAMA_FALLBACK_MODEL=qwen3.5:latest` for all tiers**; otherwise continues with catalog + heuristic scoring
- **WhatsApp not sent**: set `HERMES_ENABLED=true`, `FUTURELAB_SEND_WHATSAPP=true`, and `HERMES_WHATSAPP_GROUP`
