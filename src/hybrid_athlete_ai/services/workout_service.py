from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from hybrid_athlete_ai.models.db import (
    CrossFitPerformanceORM,
    ExerciseEntryORM,
    ExerciseSetORM,
    GoalORM,
    LiftPerformanceORM,
    RunningMetricsORM,
    TrainingSessionORM,
)
from hybrid_athlete_ai.models.exercise import ExerciseEntry, ExerciseSet, SetType
from hybrid_athlete_ai.models.goal import GoalCreate, GoalUpdate
from hybrid_athlete_ai.models.enums import DataSource, SessionType, WodFormat
from hybrid_athlete_ai.schemas.quick import QuickWorkoutCreate
from hybrid_athlete_ai.schemas.training import (
    CrossFitPerformanceCreate,
    CrossFitPerformanceRead,
    PersonalRecord,
    RunningMetricsCreate,
    RunningMetricsRead,
    TrainingSessionCreate,
    TrainingSessionRead,
    WeeklyVolume,
)
from hybrid_athlete_ai.services.crossfit_analytics import get_or_create_workout_definition
from hybrid_athlete_ai.services.quick_log import parse_run_duration, parse_strength_lines
from hybrid_athlete_ai.services.running_utils import derive_pace_sec_per_km
from hybrid_athlete_ai.services.training_analytics import calculate_volume


def _session_query(db: Session):
    return db.query(TrainingSessionORM).options(
        joinedload(TrainingSessionORM.exercises).joinedload(ExerciseEntryORM.sets),
        joinedload(TrainingSessionORM.running_metrics),
        joinedload(TrainingSessionORM.crossfit_performances).joinedload(
            CrossFitPerformanceORM.workout_definition
        ),
        joinedload(TrainingSessionORM.lift_performances),
    )


def _set_to_schema(exercise_set: ExerciseSetORM) -> ExerciseSet:
    return ExerciseSet(
        set_number=exercise_set.set_number,
        reps=exercise_set.reps,
        weight_kg=exercise_set.weight_kg,
        duration_seconds=exercise_set.duration_seconds,
        distance_meters=exercise_set.distance_meters,
        rpe=exercise_set.rpe,
        set_type=SetType(exercise_set.set_type),
        successful=exercise_set.successful,
    )


def _exercise_to_schema(exercise: ExerciseEntryORM) -> ExerciseEntry:
    return ExerciseEntry(
        name=exercise.name,
        notes=exercise.notes,
        sets=[_set_to_schema(exercise_set) for exercise_set in exercise.sets],
    )


def _running_metrics_to_read(metrics: RunningMetricsORM) -> RunningMetricsRead:
    from hybrid_athlete_ai.models.enums import RunningWorkoutType

    return RunningMetricsRead(
        id=metrics.id,
        session_id=metrics.session_id,
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


def _crossfit_performance_to_read(performance: CrossFitPerformanceORM) -> CrossFitPerformanceRead:
    from hybrid_athlete_ai.models.enums import CrossFitScoreType, RxStatus

    return CrossFitPerformanceRead(
        id=performance.id,
        session_id=performance.session_id,
        workout_definition_id=performance.workout_definition_id,
        workout_name=performance.workout_definition.name,
        workout_description=performance.workout_definition.description,
        score_type=CrossFitScoreType(performance.score_type),
        score_seconds=performance.score_seconds,
        score_reps=performance.score_reps,
        score_rounds=performance.score_rounds,
        score_load_kg=performance.score_load_kg,
        score_calories=performance.score_calories,
        score_distance_m=performance.score_distance_m,
        score_points=performance.score_points,
        score_display=performance.score_display,
        rx_status=RxStatus(performance.rx_status),
        time_cap_seconds=performance.time_cap_seconds,
        notes=performance.notes,
        created_at=performance.created_at,
    )


def _session_to_read(session: TrainingSessionORM) -> TrainingSessionRead:
    session_type = session.session_type
    try:
        session_type_enum = SessionType(session_type)
    except ValueError:
        session_type_enum = SessionType.OTHER

    return TrainingSessionRead(
        id=session.id,
        date=session.date,
        session_type=session_type_enum,
        title=session.title,
        duration_minutes=session.duration_minutes,
        notes=session.notes,
        source=DataSource(session.source),
        wod_format=WodFormat(session.wod_format) if session.wod_format else None,
        wod_description=session.wod_description,
        wod_score=session.wod_score,
        exercises=[_exercise_to_schema(exercise) for exercise in session.exercises],
        running_metrics=_running_metrics_to_read(session.running_metrics)
        if session.running_metrics
        else None,
        crossfit_performances=[
            _crossfit_performance_to_read(performance)
            for performance in session.crossfit_performances
        ],
        created_at=session.created_at,
    )


def _attach_running_metrics(
    session: TrainingSessionORM,
    metrics: RunningMetricsCreate,
) -> None:
    pace = metrics.average_pace_sec_per_km
    if pace is None:
        pace = derive_pace_sec_per_km(metrics.distance_km, metrics.duration_seconds)

    session.running_metrics = RunningMetricsORM(
        distance_km=metrics.distance_km,
        duration_seconds=metrics.duration_seconds,
        average_pace_sec_per_km=pace,
        average_hr=metrics.average_hr,
        max_hr=metrics.max_hr,
        training_load=metrics.training_load,
        elevation_gain_m=metrics.elevation_gain_m,
        average_cadence=metrics.average_cadence,
        workout_type=metrics.workout_type.value,
    )


def _attach_crossfit_performances(
    db: Session,
    session: TrainingSessionORM,
    performances: list[CrossFitPerformanceCreate],
) -> None:
    for performance in performances:
        definition = get_or_create_workout_definition(
            db,
            name=performance.workout_name,
            description=performance.workout_description,
            default_score_type=performance.score_type,
        )
        session.crossfit_performances.append(
            CrossFitPerformanceORM(
                workout_definition_id=definition.id,
                score_type=performance.score_type.value,
                score_seconds=performance.score_seconds,
                score_reps=performance.score_reps,
                score_rounds=performance.score_rounds,
                score_load_kg=performance.score_load_kg,
                score_calories=performance.score_calories,
                score_distance_m=performance.score_distance_m,
                score_points=performance.score_points,
                score_display=performance.score_display,
                rx_status=performance.rx_status.value,
                time_cap_seconds=performance.time_cap_seconds,
                notes=performance.notes,
            )
        )


def _sync_olympic_lift_performances(
    db: Session,
    session: TrainingSessionORM,
) -> None:
    if session.session_type != SessionType.OLYMPIC_LIFTING.value:
        return

    for exercise in session.exercises:
        for exercise_set in exercise.sets:
            if exercise_set.weight_kg is None or exercise_set.reps is None:
                continue
            lift = LiftPerformanceORM(
                movement=exercise.name,
                weight_kg=exercise_set.weight_kg,
                reps=exercise_set.reps,
                successful=exercise_set.successful,
                date=session.date,
                session_id=session.id,
                exercise_set_id=exercise_set.id,
            )
            db.add(lift)


def create_workout(db: Session, payload: TrainingSessionCreate) -> TrainingSessionRead:
    session = TrainingSessionORM(
        date=payload.date,
        session_type=payload.session_type.value,
        title=payload.title,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        source=payload.source.value,
        wod_format=payload.wod_format.value if payload.wod_format else None,
        wod_description=payload.wod_description,
        wod_score=payload.wod_score,
    )

    for exercise in payload.exercises:
        exercise_row = ExerciseEntryORM(name=exercise.name, notes=exercise.notes)
        for exercise_set in exercise.sets:
            exercise_row.sets.append(
                ExerciseSetORM(
                    set_number=exercise_set.set_number,
                    reps=exercise_set.reps,
                    weight_kg=exercise_set.weight_kg,
                    duration_seconds=exercise_set.duration_seconds,
                    distance_meters=exercise_set.distance_meters,
                    rpe=exercise_set.rpe,
                    set_type=exercise_set.set_type.value,
                    successful=exercise_set.successful,
                )
            )
        session.exercises.append(exercise_row)

    if payload.running_metrics:
        _attach_running_metrics(session, payload.running_metrics)

    db.add(session)
    db.flush()

    if payload.crossfit_performances:
        _attach_crossfit_performances(db, session, payload.crossfit_performances)

    _sync_olympic_lift_performances(db, session)

    db.commit()

    stored = _session_query(db).filter(TrainingSessionORM.id == session.id).one()
    return _session_to_read(stored)


def create_quick_workout(db: Session, payload: QuickWorkoutCreate) -> TrainingSessionRead:
    exercises: list[ExerciseEntry] = []
    running_metrics: RunningMetricsCreate | None = None

    if payload.strength_lines:
        exercises.extend(parse_strength_lines(payload.strength_lines))

    if payload.distance_km is not None:
        duration_seconds = parse_run_duration(payload.run_duration) if payload.run_duration else None
        if duration_seconds is not None:
            from hybrid_athlete_ai.models.enums import RunningWorkoutType

            running_metrics = RunningMetricsCreate(
                distance_km=payload.distance_km,
                duration_seconds=duration_seconds,
                workout_type=RunningWorkoutType.OTHER,
            )
        else:
            exercises.append(
                ExerciseEntry(
                    name="Run",
                    sets=[
                        ExerciseSet(
                            set_number=1,
                            distance_meters=round(payload.distance_km * 1000, 1),
                        )
                    ],
                )
            )

    full_payload = TrainingSessionCreate(
        date=payload.date,
        session_type=payload.session_type,
        title=payload.title,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        source=payload.source,
        wod_format=payload.wod_format,
        wod_description=payload.wod_description,
        wod_score=payload.wod_score,
        exercises=exercises,
        running_metrics=running_metrics,
    )
    return create_workout(db, full_payload)


def list_workouts(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    session_type: str | None = None,
    limit: int = 50,
) -> list[TrainingSessionRead]:
    query = _session_query(db)

    if start_date:
        query = query.filter(TrainingSessionORM.date >= start_date)
    if end_date:
        query = query.filter(TrainingSessionORM.date <= end_date)
    if session_type:
        query = query.filter(TrainingSessionORM.session_type == session_type)

    sessions = query.order_by(TrainingSessionORM.date.desc(), TrainingSessionORM.id.desc()).limit(limit).all()
    return [_session_to_read(session) for session in sessions]


def get_workout(db: Session, workout_id: int) -> TrainingSessionRead | None:
    session = _session_query(db).filter(TrainingSessionORM.id == workout_id).first()
    if session is None:
        return None
    return _session_to_read(session)


def get_personal_records(
    db: Session,
    *,
    exercise_name: str | None = None,
) -> list[PersonalRecord]:
    query = (
        db.query(ExerciseEntryORM, TrainingSessionORM)
        .join(TrainingSessionORM, ExerciseEntryORM.session_id == TrainingSessionORM.id)
        .options(joinedload(ExerciseEntryORM.sets))
    )

    if exercise_name:
        query = query.filter(ExerciseEntryORM.name.ilike(exercise_name))

    best_by_exercise: dict[str, PersonalRecord] = {}

    for exercise_row, session_row in query.all():
        weighted_sets = [exercise_set for exercise_set in exercise_row.sets if exercise_set.weight_kg is not None]
        if not weighted_sets:
            continue

        heaviest = max(weighted_sets, key=lambda exercise_set: exercise_set.weight_kg or 0.0)
        candidate = PersonalRecord(
            exercise_name=exercise_row.name,
            weight_kg=heaviest.weight_kg or 0.0,
            reps=heaviest.reps,
            date=session_row.date,
            session_id=session_row.id,
            session_title=session_row.title,
        )

        existing = best_by_exercise.get(exercise_row.name.lower())
        if existing is None or candidate.weight_kg > existing.weight_kg:
            best_by_exercise[exercise_row.name.lower()] = candidate

    return sorted(best_by_exercise.values(), key=lambda record: record.exercise_name.lower())


def get_weekly_volume(db: Session, *, reference_date: date | None = None) -> WeeklyVolume:
    reference_date = reference_date or date.today()
    week_start = reference_date - timedelta(days=reference_date.weekday())
    week_end = week_start + timedelta(days=6)

    sessions = (
        _session_query(db)
        .filter(TrainingSessionORM.date >= week_start, TrainingSessionORM.date <= week_end)
        .all()
    )

    total_volume = 0.0
    sessions_by_type: dict[str, int] = {}

    for session in sessions:
        sessions_by_type[session.session_type] = sessions_by_type.get(session.session_type, 0) + 1
        for exercise in session.exercises:
            total_volume += calculate_volume(_exercise_to_schema(exercise))

    return WeeklyVolume(
        week_start=week_start,
        week_end=week_end,
        total_volume_kg=total_volume,
        session_count=len(sessions),
        sessions_by_type=sessions_by_type,
    )


def create_goal(db: Session, payload: GoalCreate):
    goal = GoalORM(
        category=payload.category.value,
        title=payload.title,
        target_value=payload.target_value,
        target_unit=payload.target_unit,
        exercise_name=payload.exercise_name,
        deadline=payload.deadline,
        status=payload.status.value,
        notes=payload.notes,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def list_goals(db: Session, *, status: str | None = None):
    query = db.query(GoalORM)
    if status:
        query = query.filter(GoalORM.status == status)
    return query.order_by(GoalORM.created_at.desc()).all()


def update_goal(db: Session, goal_id: int, payload: GoalUpdate):
    goal = db.query(GoalORM).filter(GoalORM.id == goal_id).first()
    if goal is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal
