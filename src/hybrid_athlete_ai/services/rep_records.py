"""Unified rep-based PR calculation for strength sets and olympic lift performances."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session, joinedload

from hybrid_athlete_ai.models.db import (
    ExerciseEntryORM,
    ExerciseSetORM,
    LiftPerformanceORM,
    TrainingSessionORM,
)
from hybrid_athlete_ai.models.enums import SessionType
from hybrid_athlete_ai.schemas.training import RepRecord, RepRecordSummary

# Epley formula: estimated 1RM = weight × (1 + reps/30), used when reps > 1.
Epley_1RM_FORMULA = "epley"


@dataclass
class NormalizedPerformance:
    movement: str
    weight_kg: float
    reps: int
    successful: bool
    performance_date: date
    session_id: int | None
    session_title: str | None


def estimate_1rm_epley(weight_kg: float, reps: int) -> float:
    if reps <= 1:
        return weight_kg
    return weight_kg * (1 + reps / 30)


def load_strength_performances(
    db: Session,
    *,
    movement: str | None = None,
) -> list[NormalizedPerformance]:
    query = (
        db.query(ExerciseEntryORM, ExerciseSetORM, TrainingSessionORM)
        .join(ExerciseSetORM, ExerciseSetORM.exercise_id == ExerciseEntryORM.id)
        .join(TrainingSessionORM, ExerciseEntryORM.session_id == TrainingSessionORM.id)
        .filter(TrainingSessionORM.session_type == SessionType.STRENGTH.value)
    )

    if movement:
        query = query.filter(ExerciseEntryORM.name.ilike(movement))

    performances: list[NormalizedPerformance] = []
    for exercise_row, set_row, session_row in query.all():
        if set_row.weight_kg is None or set_row.reps is None:
            continue
        performances.append(
            NormalizedPerformance(
                movement=exercise_row.name,
                weight_kg=set_row.weight_kg,
                reps=set_row.reps,
                successful=set_row.successful,
                performance_date=session_row.date,
                session_id=session_row.id,
                session_title=session_row.title,
            )
        )
    return performances


def load_lift_performances(
    db: Session,
    *,
    movement: str | None = None,
) -> list[NormalizedPerformance]:
    query = db.query(LiftPerformanceORM).options(joinedload(LiftPerformanceORM.session))

    if movement:
        query = query.filter(LiftPerformanceORM.movement.ilike(movement))

    performances: list[NormalizedPerformance] = []
    for row in query.all():
        performances.append(
            NormalizedPerformance(
                movement=row.movement,
                weight_kg=row.weight_kg,
                reps=row.reps,
                successful=row.successful,
                performance_date=row.date,
                session_id=row.session_id,
                session_title=row.session.title if row.session else None,
            )
        )
    return performances


def _successful_only(performances: list[NormalizedPerformance]) -> list[NormalizedPerformance]:
    return [performance for performance in performances if performance.successful]


def _best_at_rep_count(
    performances: list[NormalizedPerformance],
    rep_count: int,
) -> NormalizedPerformance | None:
    candidates = [
        performance
        for performance in performances
        if performance.reps == rep_count
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda performance: (performance.weight_kg, performance.performance_date))


def _previous_best_at_rep_count(
    performances: list[NormalizedPerformance],
    rep_count: int,
    current: NormalizedPerformance,
) -> NormalizedPerformance | None:
    prior = [
        performance
        for performance in performances
        if performance.reps == rep_count
        and performance.performance_date < current.performance_date
        and (
            performance.performance_date != current.performance_date
            or performance.session_id != current.session_id
        )
    ]
    if not prior:
        # Same-day earlier attempt with lower weight
        prior = [
            performance
            for performance in performances
            if performance.reps == rep_count
            and performance.performance_date == current.performance_date
            and performance.weight_kg < current.weight_kg
        ]
    if not prior:
        return None
    return max(prior, key=lambda performance: performance.weight_kg)


def build_rep_record(
    current: NormalizedPerformance,
    all_performances: list[NormalizedPerformance],
    *,
    is_estimated: bool = False,
) -> RepRecord:
    previous = _previous_best_at_rep_count(all_performances, current.reps, current)
    previous_weight = previous.weight_kg if previous else None
    improvement = None
    if previous_weight is not None:
        improvement = round(current.weight_kg - previous_weight, 2)

    return RepRecord(
        movement=current.movement,
        rep_count=current.reps,
        weight_kg=round(current.weight_kg, 2),
        is_estimated=is_estimated,
        date=current.performance_date,
        session_id=current.session_id,
        session_title=current.session_title,
        previous_weight_kg=round(previous_weight, 2) if previous_weight is not None else None,
        improvement_kg=improvement,
    )


def compute_rep_records(
    performances: list[NormalizedPerformance],
    *,
    rep_counts: tuple[int, ...] = (1, 3, 5),
) -> list[RepRecord]:
    successful = _successful_only(performances)
    records: list[RepRecord] = []

    for rep_count in rep_counts:
        best = _best_at_rep_count(successful, rep_count)
        if best:
            records.append(build_rep_record(best, successful, is_estimated=False))

    return records


def compute_estimated_1rm_record(performances: list[NormalizedPerformance]) -> RepRecord | None:
    successful = _successful_only(performances)
    if not successful:
        return None

    best_estimated: NormalizedPerformance | None = None
    best_value = 0.0

    for performance in successful:
        if performance.reps <= 1:
            estimated = performance.weight_kg
        else:
            estimated = estimate_1rm_epley(performance.weight_kg, performance.reps)
        if estimated > best_value:
            best_value = estimated
            best_estimated = performance

    if best_estimated is None:
        return None

    is_estimated = best_estimated.reps > 1
    estimated_performance = NormalizedPerformance(
        movement=best_estimated.movement,
        weight_kg=round(best_value, 2),
        reps=1,
        successful=True,
        performance_date=best_estimated.performance_date,
        session_id=best_estimated.session_id,
        session_title=best_estimated.session_title,
    )
    return build_rep_record(estimated_performance, successful, is_estimated=is_estimated)


def build_rep_record_summary(
    performances: list[NormalizedPerformance],
    movement: str,
) -> RepRecordSummary:
    successful = _successful_only(performances)
    records = compute_rep_records(successful)
    estimated = compute_estimated_1rm_record(successful)

    heaviest = None
    if successful:
        heaviest_perf = max(successful, key=lambda p: p.weight_kg)
        heaviest = heaviest_perf.weight_kg

    recent = sorted(successful, key=lambda p: (p.performance_date, p.session_id or 0), reverse=True)
    recent_records = [
        RepRecord(
            movement=p.movement,
            rep_count=p.reps,
            weight_kg=round(p.weight_kg, 2),
            is_estimated=False,
            date=p.performance_date,
            session_id=p.session_id,
            session_title=p.session_title,
        )
        for p in recent[:10]
    ]

    if estimated and not any(r.rep_count == 1 and not r.is_estimated for r in records):
        records.append(estimated)

    return RepRecordSummary(
        movement=movement,
        records=records,
        heaviest_successful_set_kg=round(heaviest, 2) if heaviest is not None else None,
        estimated_1rm_kg=estimated.weight_kg if estimated else None,
        recent_history=recent_records,
    )


def get_strength_rep_summary(db: Session, exercise_name: str) -> RepRecordSummary:
    performances = load_strength_performances(db, movement=exercise_name)
    return build_rep_record_summary(performances, exercise_name)


def get_lift_rep_summary(db: Session, movement: str) -> RepRecordSummary:
    performances = load_lift_performances(db, movement=movement)
    return build_rep_record_summary(performances, movement)


def list_lift_movements(db: Session) -> list[str]:
    rows = db.query(LiftPerformanceORM.movement).distinct().all()
    return sorted({row[0] for row in rows}, key=str.lower)


def get_movement_history(db: Session, movement: str) -> list[RepRecord]:
    performances = load_lift_performances(db, movement=movement)
    successful = sorted(
        _successful_only(performances),
        key=lambda p: (p.performance_date, p.session_id or 0),
    )
    return [
        RepRecord(
            movement=p.movement,
            rep_count=p.reps,
            weight_kg=round(p.weight_kg, 2),
            is_estimated=False,
            date=p.performance_date,
            session_id=p.session_id,
            session_title=p.session_title,
        )
        for p in successful
    ]
