.PHONY: seed run serve test frontend install

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && PYTHONPATH=. python -m app.cli seed

run:
	cd backend && PYTHONPATH=. python -m app.cli run --mode auto

serve:
	cd backend && PYTHONPATH=. python -m app.cli serve

frontend:
	cd frontend && npm run dev

test:
	cd backend && PYTHONPATH=. pytest ../tests -q
