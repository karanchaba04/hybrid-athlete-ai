from sqlalchemy.orm import Session

from hybrid_athlete_ai.models.db import CrossFitPerformanceORM, TrainingSessionORM, WorkoutDefinitionORM
from hybrid_athlete_ai.models.enums import CrossFitScoreType, RxStatus
from hybrid_athlete_ai.schemas.training import CrossFitHistoryEntry, CrossFitHistorySummary, WorkoutDefinitionRead


def normalize_workout_name(name: str) -> str:
    return " ".join(name.strip().split()).lower()


def get_or_create_workout_definition(
    db: Session,
    *,
    name: str,
    description: str | None = None,
    default_score_type: CrossFitScoreType | None = None,
) -> WorkoutDefinitionORM:
    normalized = normalize_workout_name(name)
    existing = db.query(WorkoutDefinitionORM).filter(WorkoutDefinitionORM.name.ilike(name.strip())).all()
    for row in existing:
        if normalize_workout_name(row.name) == normalized:
            if description and not row.description:
                row.description = description
            if default_score_type and not row.default_score_type:
                row.default_score_type = default_score_type.value
            return row

    definition = WorkoutDefinitionORM(
        name=name.strip(),
        description=description,
        default_score_type=default_score_type.value if default_score_type else None,
    )
    db.add(definition)
    db.flush()
    return definition


def _score_value(performance: CrossFitPerformanceORM) -> float:
    score_type = CrossFitScoreType(performance.score_type)
    if score_type == CrossFitScoreType.TIME:
        return float(performance.score_seconds or 0)
    if score_type == CrossFitScoreType.ROUNDS_REPS:
        rounds = performance.score_rounds or 0
        reps = performance.score_reps or 0
        return rounds * 1000 + reps
    if score_type == CrossFitScoreType.REPS:
        return float(performance.score_reps or 0)
    if score_type == CrossFitScoreType.LOAD:
        return float(performance.score_load_kg or 0)
    if score_type == CrossFitScoreType.CALORIES:
        return float(performance.score_calories or 0)
    if score_type == CrossFitScoreType.DISTANCE:
        return float(performance.score_distance_m or 0)
    if score_type == CrossFitScoreType.POINTS:
        return float(performance.score_points or 0)
    return 0.0


def _lower_is_better(score_type: CrossFitScoreType) -> bool:
    return score_type == CrossFitScoreType.TIME


def _format_delta(score_type: CrossFitScoreType, delta: float) -> str:
    if score_type == CrossFitScoreType.TIME:
        seconds = int(abs(round(delta)))
        sign = "-" if delta < 0 else "+"
        minutes, secs = divmod(seconds, 60)
        if minutes:
            return f"{sign}{minutes}:{secs:02d}"
        return f"{sign}{secs}s"
    sign = "+" if delta > 0 else ""
    return f"{sign}{round(delta, 1)}"


def list_workout_definitions(db: Session) -> list[WorkoutDefinitionRead]:
    rows = db.query(WorkoutDefinitionORM).order_by(WorkoutDefinitionORM.name.asc()).all()
    result: list[WorkoutDefinitionRead] = []
    for row in rows:
        default_type = None
        if row.default_score_type:
            default_type = CrossFitScoreType(row.default_score_type)
        result.append(
            WorkoutDefinitionRead(
                id=row.id,
                name=row.name,
                description=row.description,
                default_score_type=default_type,
            )
        )
    return result


def get_crossfit_history(
    db: Session,
    *,
    workout_name: str | None = None,
    workout_id: int | None = None,
    rx_status: RxStatus | None = None,
) -> CrossFitHistorySummary | None:
    if workout_id is None and not workout_name:
        return None

    definition: WorkoutDefinitionORM | None = None
    if workout_id is not None:
        definition = db.query(WorkoutDefinitionORM).filter(WorkoutDefinitionORM.id == workout_id).first()
    elif workout_name:
        normalized = normalize_workout_name(workout_name)
        for row in db.query(WorkoutDefinitionORM).all():
            if normalize_workout_name(row.name) == normalized:
                definition = row
                break

    if definition is None:
        return None

    query = (
        db.query(CrossFitPerformanceORM, TrainingSessionORM)
        .join(TrainingSessionORM, CrossFitPerformanceORM.session_id == TrainingSessionORM.id)
        .filter(CrossFitPerformanceORM.workout_definition_id == definition.id)
    )
    if rx_status is not None:
        query = query.filter(CrossFitPerformanceORM.rx_status == rx_status.value)

    rows = query.order_by(TrainingSessionORM.date.asc(), CrossFitPerformanceORM.id.asc()).all()
    if not rows:
        score_type = CrossFitScoreType(definition.default_score_type or CrossFitScoreType.TIME.value)
        return CrossFitHistorySummary(
            workout_name=definition.name,
            rx_status=rx_status or RxStatus.RX,
            score_type=score_type,
            entries=[],
        )

    score_type = CrossFitScoreType(rows[0][0].score_type)
    lower_better = _lower_is_better(score_type)

    entries: list[CrossFitHistoryEntry] = []
    first_value: float | None = None
    previous_value: float | None = None

    for performance, session in rows:
        value = _score_value(performance)
        if first_value is None:
            first_value = value
        delta_prev = None
        delta_first = None
        if previous_value is not None:
            delta_prev = value - previous_value
        if first_value is not None:
            delta_first = value - first_value

        delta_display_prev = _format_delta(score_type, delta_prev) if delta_prev is not None else None

        entries.append(
            CrossFitHistoryEntry(
                date=session.date,
                session_id=session.id,
                performance_id=performance.id,
                workout_name=definition.name,
                score_type=score_type,
                score_seconds=performance.score_seconds,
                score_reps=performance.score_reps,
                score_rounds=performance.score_rounds,
                score_load_kg=performance.score_load_kg,
                score_calories=performance.score_calories,
                score_distance_m=performance.score_distance_m,
                score_points=performance.score_points,
                score_display=performance.score_display,
                rx_status=RxStatus(performance.rx_status),
                delta_from_previous=delta_prev,
                delta_from_first=delta_first,
                delta_display=delta_display_prev,
            )
        )
        previous_value = value

    # Return most recent first for UI
    entries.reverse()

    resolved_rx = rx_status or RxStatus(rows[-1][0].rx_status)

    return CrossFitHistorySummary(
        workout_name=definition.name,
        rx_status=resolved_rx,
        score_type=score_type,
        entries=entries,
    )
