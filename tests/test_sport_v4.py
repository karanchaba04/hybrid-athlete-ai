from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import hybrid_athlete_ai.models.db  # noqa: F401
from hybrid_athlete_ai.database import Base
from hybrid_athlete_ai.models.enums import (
    CrossFitScoreType,
    RunningWorkoutType,
    RxStatus,
    SessionType,
)
from hybrid_athlete_ai.models.exercise import ExerciseEntry, ExerciseSet
from hybrid_athlete_ai.schemas.training import CrossFitPerformanceCreate, RunningMetricsCreate, TrainingSessionCreate
from hybrid_athlete_ai.services import workout_service
from hybrid_athlete_ai.services.crossfit_analytics import get_crossfit_history
from hybrid_athlete_ai.services.rep_records import (
    estimate_1rm_epley,
    get_lift_rep_summary,
    get_movement_history,
    get_strength_rep_summary,
)
from hybrid_athlete_ai.services.running_analytics import get_running_history
from hybrid_athlete_ai.services.running_utils import derive_pace_sec_per_km


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_derive_pace():
    pace = derive_pace_sec_per_km(8.0, 2472)
    assert pace == 309.0


def test_running_metrics_persistence_and_nullable_fields(db_session):
    payload = TrainingSessionCreate(
        date=date.today(),
        session_type=SessionType.RUNNING,
        title="Threshold run",
        running_metrics=RunningMetricsCreate(
            distance_km=8.0,
            duration_seconds=2472,
            average_hr=168,
            max_hr=181,
            workout_type=RunningWorkoutType.THRESHOLD,
        ),
    )
    created = workout_service.create_workout(db_session, payload)
    assert created.running_metrics is not None
    assert created.running_metrics.average_pace_sec_per_km == 309.0
    assert created.running_metrics.average_hr == 168
    assert created.running_metrics.training_load is None


def test_legacy_running_fallback(db_session):
    payload = TrainingSessionCreate(
        date=date.today(),
        session_type=SessionType.RUNNING,
        title="Legacy run",
        exercises=[
            ExerciseEntry(
                name="Run",
                sets=[
                    ExerciseSet(set_number=1, distance_meters=8000, duration_seconds=2400),
                ],
            )
        ],
    )
    workout_service.create_workout(db_session, payload)
    history = get_running_history(db_session, weeks=1)
    assert len(history) == 1
    assert history[0].distance_km == 8.0


def test_strength_rep_records(db_session):
    for day_offset, weight in [(14, 100), (7, 105), (0, 110)]:
        workout_service.create_workout(
            db_session,
            TrainingSessionCreate(
                date=date.today() - timedelta(days=day_offset),
                session_type=SessionType.STRENGTH,
                title="Squat",
                exercises=[
                    ExerciseEntry(
                        name="Back Squat",
                        sets=[ExerciseSet(set_number=1, reps=5, weight_kg=weight)],
                    )
                ],
            ),
        )

    summary = get_strength_rep_summary(db_session, "Back Squat")
    five_rm = next(record for record in summary.records if record.rep_count == 5)
    assert five_rm.weight_kg == 110
    assert five_rm.is_estimated is False
    assert five_rm.previous_weight_kg == 105
    assert five_rm.improvement_kg == 5


def test_estimated_1rm_distinct_from_actual(db_session):
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date.today(),
            session_type=SessionType.STRENGTH,
            title="Press day",
            exercises=[
                ExerciseEntry(
                    name="Strict Press",
                    sets=[ExerciseSet(set_number=1, reps=5, weight_kg=60)],
                )
            ],
        ),
    )
    summary = get_strength_rep_summary(db_session, "Strict Press")
    assert summary.estimated_1rm_kg == round(estimate_1rm_epley(60, 5), 2)
    one_rm_records = [r for r in summary.records if r.rep_count == 1]
    assert not one_rm_records or one_rm_records[0].is_estimated


def test_olympic_lift_performances_and_failed_attempts(db_session):
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date.today(),
            session_type=SessionType.OLYMPIC_LIFTING,
            title="Oly day",
            exercises=[
                ExerciseEntry(
                    name="Snatch",
                    sets=[
                        ExerciseSet(set_number=1, reps=1, weight_kg=47.5, successful=True),
                        ExerciseSet(set_number=2, reps=1, weight_kg=50, successful=True),
                        ExerciseSet(set_number=3, reps=1, weight_kg=52.5, successful=False),
                    ],
                )
            ],
        ),
    )

    summary = get_lift_rep_summary(db_session, "Snatch")
    one_rm = next(record for record in summary.records if record.rep_count == 1)
    assert one_rm.weight_kg == 50

    history = get_movement_history(db_session, "Snatch")
    assert len(history) == 2


def test_crossfit_history_comparison(db_session):
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date(2025, 12, 3),
            session_type=SessionType.CROSSFIT,
            title="Fran day",
            crossfit_performances=[
                CrossFitPerformanceCreate(
                    workout_name="Fran",
                    score_type=CrossFitScoreType.TIME,
                    score_seconds=357,
                    rx_status=RxStatus.RX,
                )
            ],
        ),
    )
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date(2026, 5, 10),
            session_type=SessionType.CROSSFIT,
            title="Fran again",
            crossfit_performances=[
                CrossFitPerformanceCreate(
                    workout_name="Fran",
                    score_type=CrossFitScoreType.TIME,
                    score_seconds=321,
                    rx_status=RxStatus.RX,
                )
            ],
        ),
    )
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date(2026, 8, 19),
            session_type=SessionType.CROSSFIT,
            title="Fran PR",
            crossfit_performances=[
                CrossFitPerformanceCreate(
                    workout_name="Fran",
                    score_type=CrossFitScoreType.TIME,
                    score_seconds=288,
                    rx_status=RxStatus.RX,
                )
            ],
        ),
    )

    summary = get_crossfit_history(db_session, workout_name="Fran", rx_status=RxStatus.RX)
    assert summary is not None
    assert len(summary.entries) == 3
    assert summary.entries[0].score_seconds == 288
    assert summary.entries[0].delta_from_previous == -33


def test_crossfit_rx_vs_scaled_separate(db_session):
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date.today(),
            session_type=SessionType.CROSSFIT,
            title="Cindy rx",
            crossfit_performances=[
                CrossFitPerformanceCreate(
                    workout_name="Cindy",
                    score_type=CrossFitScoreType.ROUNDS_REPS,
                    score_rounds=15,
                    score_reps=7,
                    rx_status=RxStatus.RX,
                )
            ],
        ),
    )
    workout_service.create_workout(
        db_session,
        TrainingSessionCreate(
            date=date.today() - timedelta(days=1),
            session_type=SessionType.CROSSFIT,
            title="Cindy scaled",
            crossfit_performances=[
                CrossFitPerformanceCreate(
                    workout_name="Cindy",
                    score_type=CrossFitScoreType.ROUNDS_REPS,
                    score_rounds=12,
                    score_reps=3,
                    rx_status=RxStatus.SCALED,
                )
            ],
        ),
    )

    rx_summary = get_crossfit_history(db_session, workout_name="Cindy", rx_status=RxStatus.RX)
    scaled_summary = get_crossfit_history(db_session, workout_name="Cindy", rx_status=RxStatus.SCALED)
    assert rx_summary.entries[0].score_rounds == 15
    assert scaled_summary.entries[0].score_rounds == 12
