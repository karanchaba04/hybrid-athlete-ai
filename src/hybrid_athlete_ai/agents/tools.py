import json
from datetime import date
from typing import Any

from langchain_core.tools import tool

from hybrid_athlete_ai.database import SessionLocal
from hybrid_athlete_ai.mcp import tools as data_tools


def _json_result(data: Any) -> str:
    return json.dumps(data, default=str)


@tool
def get_recent_workouts(
    limit: int = 10,
    session_type: str | None = None,
    weeks: int | None = None,
) -> str:
    """List recent training sessions. Optional session_type filter (strength, running, crossfit, etc.) and weeks lookback."""
    db = SessionLocal()
    try:
        return _json_result(
            data_tools.get_recent_workouts(
                db,
                limit=limit,
                session_type=session_type,
                weeks=weeks,
            )
        )
    finally:
        db.close()


@tool
def get_workout(workout_id: int) -> str:
    """Get one workout session by ID, including exercises and sets."""
    db = SessionLocal()
    try:
        result = data_tools.get_workout_by_id(db, workout_id)
        return _json_result(result if result is not None else {"error": "Workout not found"})
    finally:
        db.close()


@tool
def get_personal_records(exercise_name: str | None = None) -> str:
    """Get personal records (heaviest set per exercise). Optional exercise_name filter."""
    db = SessionLocal()
    try:
        return _json_result(data_tools.get_personal_records(db, exercise_name=exercise_name))
    finally:
        db.close()


@tool
def get_weekly_volume(reference_date: str | None = None) -> str:
    """Get this week's training volume (kg) and session counts by type. reference_date is ISO date optional."""
    parsed = date.fromisoformat(reference_date) if reference_date else None
    db = SessionLocal()
    try:
        return _json_result(data_tools.get_weekly_volume(db, reference_date=parsed))
    finally:
        db.close()


@tool
def get_current_goals() -> str:
    """List active training goals."""
    db = SessionLocal()
    try:
        return _json_result(data_tools.get_current_goals(db))
    finally:
        db.close()


@tool
def get_strength_history(exercise_name: str, weeks: int = 12) -> str:
    """Strength history for one exercise — heaviest set per session over recent weeks (e.g. back squat, strict press)."""
    db = SessionLocal()
    try:
        return _json_result(
            data_tools.get_strength_history_tool(
                db,
                exercise_name=exercise_name,
                weeks=weeks,
            )
        )
    finally:
        db.close()


@tool
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
) -> str:
    """Log a workout using quick shorthand. Only use when user explicitly requests logging. strength_lines e.g. 'Strict Press: 40x5, 50x3'."""
    db = SessionLocal()
    try:
        return _json_result(
            data_tools.log_workout_quick(
                db,
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
        )
    finally:
        db.close()


COACH_TOOLS = [
    get_recent_workouts,
    get_workout,
    get_personal_records,
    get_weekly_volume,
    get_current_goals,
    get_strength_history,
    log_workout_quick,
]
