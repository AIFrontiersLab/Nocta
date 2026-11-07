# API

Base URL: `http://127.0.0.1:8787/api`

## Core

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/home` | Morning dashboard payload |
| GET | `/signals` | Collected signals |
| GET | `/convergences` | Detected convergences |
| GET | `/ideas` | Idea list (`?status=`) |
| GET | `/ideas/{id}` | Idea detail |
| GET | `/prototypes` | Built prototypes |
| GET | `/runs` | Experiment runs |
| GET | `/runs/{id}` | Run detail + timeline |
| POST | `/runs/start` | Start a run |
| POST | `/ideas/{id}/feedback` | Human feedback |

## Analytics

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/analytics/overview` | Summary, trends, tech tags |
| GET | `/analytics/evaluation` | Obvious-filter eval suite |
