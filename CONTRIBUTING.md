# Contributing

## Local setup

1. Copy `.env.example` → `.env`
2. Backend: create venv, `pip install -r backend/requirements.txt`
3. Frontend: `npm install` in `frontend/`
4. Seed: `PYTHONPATH=. python -m app.cli seed` from `backend/`
5. Run tests: `cd backend && PYTHONPATH=. pytest ../tests -q`

## Guidelines

- Keep overnight runs bounded (`MAX_MODEL_CALLS`, `MAX_RUNTIME_MINUTES`)
- Prefer adapter modules over inlining new signal sources
- Do not commit `.env`, tokens, or `outputs/` artifacts
- Add unit tests for scoring/filter/analytics changes
