from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from hybrid_athlete_ai.models.db import ExerciseEntryORM, RunningMetricsORM, TrainingSessionORM
from hybrid_athlete_ai.models.enums import RunningWorkoutType, SessionType
from hybrid_athlete_ai.schemas.training import RunningHistoryEntry
from hybrid_athlete_ai.services.running_utils import derive_pace_sec_per_km


def _legacy_running_from_exercises(session: TrainingSessionORM) -> RunningHistoryEntry | None:
    for exercise in session.exercises:
        if exercise.name.lower() != "run":
            continue
        for exercise_set in exercise.sets:
            if exercise_set.distance_meters is None:
                continue
            distance_km = exercise_set.distance_meters / 1000.0
            duration = exercise_set.duration_seconds or 0
            if duration <= 0:
                continue
            pace = derive_pace_sec_per_km(distance_km, duration)
            return RunningHistoryEntry(
                date=session.date,
                session_id=session.id,
                session_title=session.title,
                distance_km=round(distance_km, 3),
                duration_seconds=duration,
                average_pace_sec_per_km=pace,
                workout_type=RunningWorkoutType.OTHER,
            )
    return None


def _metrics_to_entry(
    session: TrainingSessionORM,
    metrics: RunningMetricsORM,
) -> RunningHistoryEntry:
    return RunningHistoryEntry(
        date=session.date,
        session_id=session.id,
        session_title=session.title,
        distance_km=metrics.distance_km,
        duration_seconds=metrics.duration_seconds,
        average_pace_sec_per_km=metrics.average_pace_sec_per_km,
        average_hr=metrics.average_hr,
        max_hr=metrics.max_hr,
        training_load=metrics.training_load,
        elevation_gain_m=metrics.elevation_gain_m,
        average_cadence=metrics.average_cadence,
        workout_type=RunningWorkoutType(metrics.workout_type),
    )


def get_running_history(
    db: Session,
    *,
    weeks: int = 12,
    limit: int = 50,
) -> list[RunningHistoryEntry]:
    start_date = date.today() - timedelta(weeks=weeks)

    sessions = (
        db.query(TrainingSessionORM)
        .options(
            joinedload(TrainingSessionORM.running_metrics),
            joinedload(TrainingSessionORM.exercises).joinedload(ExerciseEntryORM.sets),
        )
        .filter(
            TrainingSessionORM.session_type == SessionType.RUNNING.value,
            TrainingSessionORM.date >= start_date,
        )
        .order_by(TrainingSessionORM.date.desc(), TrainingSessionORM.id.desc())
        .limit(limit)
        .all()
    )

    entries: list[RunningHistoryEntry] = []
    for session in sessions:
        if session.running_metrics:
            entries.append(_metrics_to_entry(session, session.running_metrics))
        else:
            legacy = _legacy_running_from_exercises(session)
            if legacy:
                entries.append(legacy)

    return entries
