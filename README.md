# Hybrid Athlete AI

Personal training operating system that unifies fragmented training data and eventually powers an AI coach via MCP + LangGraph.

## Current status

**V1 — Training tracker**, **V2 — MCP server**, **V3 — LangGraph coach**, and **V4 — Web UI** are working.

```text
Browser (Next.js) → FastAPI → SQLAlchemy → analytics / MCP / LangGraph coach
```

### What's working

- FastAPI API for logging workouts and goals (including quick-log shorthand)
- SQLite database (PostgreSQL-ready via `DATABASE_URL`)
- Session types: strength, running, crossfit, hyrox, olympic_lifting, skills, recovery, other
- Analytics: personal records, weekly volume, strength history
- MCP server (stdio) for testing with Claude Desktop / Cursor
- LangGraph ReAct coach at `POST /api/v1/coach/chat` (Claude / Anthropic)
- LangGraph accessory planner at `POST /api/v1/coach/accessories` (V3.1)
- Next.js web app: dashboard, workout logging, AI coach, history/analytics

### Project structure

```text
hybrid-athlete-ai/
├── src/hybrid_athlete_ai/
│   ├── api/           # FastAPI routes
│   ├── models/        # Pydantic domain models + SQLAlchemy ORM
│   ├── schemas/       # API request/response shapes
│   ├── services/      # Business logic and analytics
│   ├── mcp/           # V2 — MCP server
│   ├── agents/        # V3 — LangGraph coach
│   ├── config.py
│   ├── database.py
│   └── main.py
├── web/               # V4 — Next.js UI
├── tests/
├── pyproject.toml
└── README.md
```

### Roadmap

| Release | Focus |
|---------|-------|
| **V1** | Training tracker |
| **V2** | MCP server |
| **V3** | LangGraph AI coach (V3.0 chat + V3.1 accessory planner) |
| **V4** | Web application UI + deployment |
| **V5** | Real external integration (e.g. Strava) |
| **V6** | RAG over coaching knowledge + deeper intelligence |

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

## Web UI (V4)

Next.js + TypeScript + Tailwind frontend for dashboard, workout logging, AI coach, and history.

```bash
cd web
cp .env.local.example .env.local   # optional; defaults to http://127.0.0.1:8000/api/v1
npm install
npm run dev
```

Run the API and UI together (two terminals):

```bash
uv run hybrid-athlete-ai          # http://127.0.0.1:8000
cd web && npm run dev               # http://localhost:3000
```

| Screen | Route | Backend |
|--------|-------|---------|
| Dashboard | `/` | weekly volume, goals, recent workouts |
| Log workout | `/log` | `POST /workouts` |
| AI coach | `/coach` | `POST /coach/chat`, `POST /coach/accessories` |
| History | `/history` | sessions, PRs, strength history chart |

## Quick log (easier than nested JSON)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/workouts/quick \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-08-14",
    "session_type": "strength",
    "title": "Upper Body",
    "strength_lines": [
      "Strict Press: 40x5, 50x3, 30x8",
      "Back Squat: 100x5x3"
    ]
  }'
```

## MCP server (V2 — for testing with Claude Desktop / Cursor)

Run manually:

```bash
uv run hybrid-athlete-mcp
```

### Claude Desktop config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hybrid-athlete": {
      "command": "uv",
      "args": ["run", "hybrid-athlete-mcp"],
      "cwd": "/Users/karanchaba/Projects/hybrid-athlete-ai"
    }
  }
}
```

Restart Claude Desktop. You should see tools like `get_recent_workouts`, `get_personal_records`, `get_strength_history`, `log_workout_quick`.

### MCP tools

| Tool | Purpose |
|------|---------|
| `get_recent_workouts` | Recent sessions, optional type/week filter |
| `get_workout` | Single session by ID |
| `get_personal_records` | PRs by exercise |
| `get_weekly_volume` | This week's volume |
| `get_current_goals` | Active goals |
| `get_strength_history` | Exercise trend over weeks |
| `log_workout_quick` | Log via shorthand lines |
| `create_goal` | Add a goal |

### Example prompts (after logging some workouts)

- "What workouts did I log this week?"
- "What's my PR for back squat?"
- "How has my strict press progressed over the last month?"

## AI coach (V3)

Add your Anthropic (Claude) API key to `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
COACH_MODEL=claude-sonnet-5
```

Chat with the coach (uses your training DB via tools):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/coach/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What workouts did I log this week?", "thread_id": "my-session"}'
```

Use the same `thread_id` for multi-turn conversation memory.

Example questions:

- "How has my back squat progressed over the last month?"
- "What's my strict press PR?"
- "What should I focus on based on my goals and this week's training?"

### Accessory planner (V3.1)

Structured multi-step graph: gathers goals, weekly load, and strength snapshots, then recommends per slot.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/coach/accessories \
  -H "Content-Type: application/json" \
  -d '{
    "available_slots": ["Tue 30 min", "Thu 45 min", "Sat 30 min"],
    "notes": "Shoulder feels tight; gym has heavy squats in CF this week"
  }'
```

Returns `recommendation` (structured slots + rationale) and `context_summary` (the data the coach used).

## Tests

```bash
uv run pytest
```
