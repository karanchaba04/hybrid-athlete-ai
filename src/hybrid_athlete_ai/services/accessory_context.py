from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from hybrid_athlete_ai.models.enums import SessionType
from hybrid_athlete_ai.models.goal import Goal, GoalStatus
from hybrid_athlete_ai.services import workout_service
from hybrid_athlete_ai.services.strength_history import get_strength_history

_LOAD_RELEVANT_TYPES = {
    SessionType.STRENGTH.value,
    SessionType.CROSSFIT.value,
    SessionType.HYROX.value,
    SessionType.OLYMPIC_LIFTING.value,
    SessionType.SKILLS.value,
}

_SQUAT_KEYWORDS = ("squat", "lunge")
_PRESS_KEYWORDS = ("press", "push press", "strict press", "bench")
_PULL_KEYWORDS = ("pull", "row", "chin", "pull-up", "pull up")


def _serialize_workout(workout) -> dict[str, Any]:
    return {
        "id": workout.id,
        "date": workout.date.isoformat(),
        "session_type": workout.session_type,
        "title": workout.title,
        "duration_minutes": workout.duration_minutes,
        "wod_description": workout.wod_description,
        "exercises": [
            {
                "name": exercise.name,
                "sets": [
                    {
                        "reps": exercise_set.reps,
                        "weight_kg": exercise_set.weight_kg,
                    }
                    for exercise_set in exercise.sets
                ],
            }
            for exercise in workout.exercises
        ],
    }


def _count_keyword_sessions(workouts: list, keywords: tuple[str, ...]) -> int:
    count = 0
    for workout in workouts:
        text = f"{workout.title} {' '.join(ex.name.lower() for ex in workout.exercises)}".lower()
        if any(keyword in text for keyword in keywords):
            count += 1
    return count


def build_accessory_context(db: Session) -> dict[str, Any]:
    """Gather deterministic context for accessory programming."""
    weekly_volume = workout_service.get_weekly_volume(db)
    recent_workouts = workout_service.list_workouts(
        db,
        start_date=date.today() - timedelta(days=14),
        limit=40,
    )

    load_relevant = [
        workout for workout in recent_workouts if workout.session_type.value in _LOAD_RELEVANT_TYPES
    ]
    this_week = [
        workout
        for workout in load_relevant
        if workout.date >= weekly_volume.week_start and workout.date <= weekly_volume.week_end
    ]

    goals = [
        Goal.model_validate(goal).model_dump(mode="json")
        for goal in workout_service.list_goals(db, status=GoalStatus.ACTIVE.value)
    ]

    strength_snapshots: dict[str, list[dict[str, Any]]] = {}
    for goal in goals:
        exercise_name = goal.get("exercise_name")
        if not exercise_name:
            continue
        history = get_strength_history(db, exercise_name=exercise_name, weeks=8)
        strength_snapshots[exercise_name] = [entry.model_dump(mode="json") for entry in history[-5:]]

    return {
        "week_start": weekly_volume.week_start.isoformat(),
        "week_end": weekly_volume.week_end.isoformat(),
        "weekly_volume": weekly_volume.model_dump(mode="json"),
        "active_goals": goals,
        "recent_workouts": [_serialize_workout(workout) for workout in load_relevant[:15]],
        "this_week_sessions": [_serialize_workout(workout) for workout in this_week],
        "load_signals": {
            "squat_pattern_sessions_this_week": _count_keyword_sessions(this_week, _SQUAT_KEYWORDS),
            "press_pattern_sessions_this_week": _count_keyword_sessions(this_week, _PRESS_KEYWORDS),
            "pull_pattern_sessions_this_week": _count_keyword_sessions(this_week, _PULL_KEYWORDS),
        },
        "strength_snapshots": strength_snapshots,
        "programming_note": (
            "SugarWOD / external gym programming is not connected yet. "
            "Use logged CrossFit and strength sessions as the weekly programming signal."
        ),
    }
