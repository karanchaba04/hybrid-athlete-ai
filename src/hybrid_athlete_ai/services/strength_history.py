from datetime import date, timedelta

from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from hybrid_athlete_ai.models.db import ExerciseEntryORM, TrainingSessionORM


class StrengthHistoryEntry(BaseModel):
    date: date
    session_id: int
    session_title: str
    exercise_name: str
    best_weight_kg: float
    reps_at_best: int | None = None


def get_strength_history(
    db: Session,
    *,
    exercise_name: str,
    weeks: int = 12,
) -> list[StrengthHistoryEntry]:
    """Heaviest weighted set per session for a given exercise over recent weeks."""
    start_date = date.today() - timedelta(weeks=weeks)

    rows = (
        db.query(ExerciseEntryORM, TrainingSessionORM)
        .join(TrainingSessionORM, ExerciseEntryORM.session_id == TrainingSessionORM.id)
        .options(joinedload(ExerciseEntryORM.sets))
        .filter(
            TrainingSessionORM.date >= start_date,
            ExerciseEntryORM.name.ilike(exercise_name),
        )
        .order_by(TrainingSessionORM.date.asc(), TrainingSessionORM.id.asc())
        .all()
    )

    history: list[StrengthHistoryEntry] = []

    for exercise_row, session_row in rows:
        weighted_sets = [
            exercise_set for exercise_set in exercise_row.sets if exercise_set.weight_kg is not None
        ]
        if not weighted_sets:
            continue

        heaviest = max(weighted_sets, key=lambda exercise_set: exercise_set.weight_kg or 0.0)
        history.append(
            StrengthHistoryEntry(
                date=session_row.date,
                session_id=session_row.id,
                session_title=session_row.title,
                exercise_name=exercise_row.name,
                best_weight_kg=heaviest.weight_kg or 0.0,
                reps_at_best=heaviest.reps,
            )
        )

    return history
