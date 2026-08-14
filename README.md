# Hybrid Athlete AI

Personal training operating system that unifies fragmented training data and eventually powers an AI coach via MCP + LangGraph.

## Current status: V1 — Training Tracker

This release proves the core loop:

```text
Workout entered → Stored → Analyzed → (later) MCP exposes data → LLM reasons over it
```

### What's working

- FastAPI API for logging workouts and goals
- SQLite database (PostgreSQL-ready via `DATABASE_URL`)
- Domain models for strength, running, CrossFit, Hyrox, accessories
- Analytics: personal records and weekly volume

### Project structure

```text
hybrid-athlete-ai/
├── src/hybrid_athlete_ai/
│   ├── api/           # FastAPI routes
│   ├── models/        # Pydantic domain models + SQLAlchemy ORM
│   ├── schemas/       # API request/response shapes
│   ├── services/      # Business logic and analytics
│   ├── mcp/           # V2 — MCP server (placeholder)
│   ├── agents/        # V3 — LangGraph coach (placeholder)
│   ├── config.py
│   ├── database.py
│   └── main.py
├── tests/
├── pyproject.toml
└── README.md
```

### Roadmap

| Release | Focus |
|---------|-------|
| **V1** | Training tracker (this) |
| **V2** | MCP server exposing athlete tools |
| **V3** | LangGraph AI coach |
| **V4** | RAG over training knowledge |
| **V5** | External integrations (Garmin, Strava, SugarWOD, Google Sheets) |
| **V6** | Dashboard UI + deployment |

## Setup

```bash
uv sync
cp .env.example .env
```

## Run the API

```bash
uv run hybrid-athlete-ai
# or
uv run uvicorn hybrid_athlete_ai.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs.

## Example: log a workout

```bash
curl -X POST http://127.0.0.1:8000/api/v1/workouts \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-08-14",
    "session_type": "strength",
    "title": "Lower Body Strength",
    "duration_minutes": 75,
    "exercises": [
      {
        "name": "Back Squat",
        "sets": [
          {"set_number": 1, "reps": 5, "weight_kg": 80},
          {"set_number": 2, "reps": 5, "weight_kg": 90},
          {"set_number": 3, "reps": 5, "weight_kg": 100}
        ]
      }
    ]
  }'
```

## Example: check PRs and weekly volume

```bash
curl "http://127.0.0.1:8000/api/v1/analytics/prs?exercise_name=Back%20Squat"
curl "http://127.0.0.1:8000/api/v1/analytics/weekly-volume"
```

## Tests

```bash
uv run pytest
```
