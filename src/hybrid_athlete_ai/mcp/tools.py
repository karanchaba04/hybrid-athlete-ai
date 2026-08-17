"""MCP tool handlers — thin wrappers over workout_service and analytics."""

from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from hybrid_athlete_ai.models.enums import SessionType
from hybrid_athlete_ai.models.goal import Goal, GoalCreate, GoalCategory, GoalStatus
from hybrid_athlete_ai.schemas.quick import QuickWorkoutCreate
from hybrid_athlete_ai.services import workout_service
from hybrid_athlete_ai.services.strength_history import get_strength_history


def _dump(model: Any) -> Any:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    if isinstance(model, list):
        return [_dump(item) for item in model]
    return model


def get_recent_workouts(
    db: Session,
    *,
    limit: int = 10,
    session_type: str | None = None,
    weeks: int | None = None,
) -> list[dict[str, Any]]:
    start_date = None
    if weeks is not None:
        start_date = date.today() - timedelta(weeks=weeks)

    workouts = workout_service.list_workouts(
        db,
        start_date=start_date,
        session_type=session_type,
        limit=limit,
    )
    return [_dump(workout) for workout in workouts]


def get_workout_by_id(db: Session, workout_id: int) -> dict[str, Any] | None:
    workout = workout_service.get_workout(db, workout_id)
    return _dump(workout) if workout else None


def get_personal_records(
    db: Session,
    *,
    exercise_name: str | None = None,
) -> list[dict[str, Any]]:
    records = workout_service.get_personal_records(db, exercise_name=exercise_name)
    return [_dump(record) for record in records]


def get_weekly_volume(db: Session, reference_date: date | None = None) -> dict[str, Any]:
    volume = workout_service.get_weekly_volume(db, reference_date=reference_date)
    return _dump(volume)


def get_current_goals(db: Session) -> list[dict[str, Any]]:
    goals = workout_service.list_goals(db, status=GoalStatus.ACTIVE.value)
    return [Goal.model_validate(goal).model_dump(mode="json") for goal in goals]


def get_strength_history_tool(
    db: Session,
    *,
    exercise_name: str,
    weeks: int = 12,
) -> list[dict[str, Any]]:
    entries = get_strength_history(db, exercise_name=exercise_name, weeks=weeks)
    return [_dump(entry) for entry in entries]


def log_workout_quick(
    db: Session,
    *,
    workout_date: date,
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
) -> dict[str, Any]:
    from hybrid_athlete_ai.models.enums import WodFormat

    payload = QuickWorkoutCreate(
        date=workout_date,
        session_type=SessionType(session_type),
        title=title,
        duration_minutes=duration_minutes,
        notes=notes,
        strength_lines=strength_lines or [],
        distance_km=distance_km,
        run_duration=run_duration,
        wod_format=WodFormat(wod_format) if wod_format else None,
        wod_description=wod_description,
        wod_score=wod_score,
    )
    workout = workout_service.create_quick_workout(db, payload)
    return _dump(workout)


def create_goal_tool(
    db: Session,
    *,
    category: str,
    title: str,
    target_value: float | None = None,
    target_unit: str | None = None,
    exercise_name: str | None = None,
    deadline: date | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    goal = workout_service.create_goal(
        db,
        GoalCreate(
            category=GoalCategory(category),
            title=title,
            target_value=target_value,
            target_unit=target_unit,
            exercise_name=exercise_name,
            deadline=deadline,
            notes=notes,
        ),
    )
    return Goal.model_validate(goal).model_dump(mode="json")
