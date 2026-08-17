"""Hybrid Athlete MCP server — stdio transport for Claude Desktop / Cursor testing."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date

from mcp.server.mcpserver import MCPServer

from hybrid_athlete_ai.database import SessionLocal, init_db
from hybrid_athlete_ai.mcp import tools as athlete_tools

INSTRUCTIONS = """
You have access to Karan's Hybrid Athlete training database.

Use these tools for factual training data (workouts, PRs, volume, goals).
Do not guess weights, volumes, or progress — call the appropriate tool first.

Session types: strength, running, crossfit, hyrox, olympic_lifting, skills, recovery, other.

Strength quick-log lines use: "Exercise Name: 40x5, 50x3, 30x8" or "Back Squat: 100x5x3".
"""


@asynccontextmanager
async def lifespan(_: MCPServer) -> AsyncIterator[None]:
    init_db()
    yield


mcp = MCPServer(
    "hybrid-athlete",
    title="Hybrid Athlete AI",
    instructions=INSTRUCTIONS,
    lifespan=lifespan,
)


def _with_db(handler):
    """Run a sync handler with a DB session."""

    def wrapper(**kwargs):
        db = SessionLocal()
        try:
            return handler(db, **kwargs)
        finally:
            db.close()

    return wrapper


@mcp.tool(
    description="List recent training sessions. Optionally filter by session_type or limit to recent weeks.",
)
def get_recent_workouts(
    limit: int = 10,
    session_type: str | None = None,
    weeks: int | None = None,
) -> list[dict]:
    return _with_db(athlete_tools.get_recent_workouts)(
        limit=limit,
        session_type=session_type,
        weeks=weeks,
    )


@mcp.tool(description="Get a single workout session by ID, including exercises and sets.")
def get_workout(workout_id: int) -> dict | None:
    return _with_db(athlete_tools.get_workout_by_id)(workout_id=workout_id)


@mcp.tool(description="Get personal records (heaviest set per exercise). Optional exercise_name filter.")
def get_personal_records(exercise_name: str | None = None) -> list[dict]:
    return _with_db(athlete_tools.get_personal_records)(exercise_name=exercise_name)


@mcp.tool(description="Get this week's training volume and session counts by type.")
def get_weekly_volume(reference_date: str | None = None) -> dict:
    parsed_date = date.fromisoformat(reference_date) if reference_date else None
    return _with_db(athlete_tools.get_weekly_volume)(reference_date=parsed_date)


@mcp.tool(description="List active training goals.")
def get_current_goals() -> list[dict]:
    return _with_db(athlete_tools.get_current_goals)()


@mcp.tool(
    description=(
        "Strength history for one exercise over recent weeks. "
        "Returns the heaviest set from each session (e.g. back squat, strict press)."
    ),
)
def get_strength_history(exercise_name: str, weeks: int = 12) -> list[dict]:
    return _with_db(athlete_tools.get_strength_history_tool)(
        exercise_name=exercise_name,
        weeks=weeks,
    )


@mcp.tool(
    description=(
        "Log a workout using quick shorthand. "
        "strength_lines examples: 'Strict Press: 40x5, 50x3, 30x8' or 'Back Squat: 100x5x3'. "
        "For runs set distance_km and run_duration (e.g. '24:30'). "
        "For WODs set wod_format, wod_description, wod_score."
    ),
)
def log_workout_quick(
    workout_date: str,
    session_type: str,
    title: str,
    strength_lines: list[str] | None = None,
    distance_km: float | None = None,
    run_duration: str | None = None,
    wod_format: str | None = None,
    wod_description: str | None = None,
    wod_score: str | None = None,
    duration_minutes: int | None = None,
    notes: str | None = None,
) -> dict:
    return _with_db(athlete_tools.log_workout_quick)(
        workout_date=date.fromisoformat(workout_date),
        session_type=session_type,
        title=title,
        strength_lines=strength_lines,
        distance_km=distance_km,
        run_duration=run_duration,
        wod_format=wod_format,
        wod_description=wod_description,
        wod_score=wod_score,
        duration_minutes=duration_minutes,
        notes=notes,
    )


@mcp.tool(description="Create a new training goal.")
def create_goal(
    category: str,
    title: str,
    target_value: float | None = None,
    target_unit: str | None = None,
    exercise_name: str | None = None,
    deadline: str | None = None,
    notes: str | None = None,
) -> dict:
    parsed_deadline = date.fromisoformat(deadline) if deadline else None
    return _with_db(athlete_tools.create_goal_tool)(
        category=category,
        title=title,
        target_value=target_value,
        target_unit=target_unit,
        exercise_name=exercise_name,
        deadline=parsed_deadline,
        notes=notes,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
