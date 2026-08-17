from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import hybrid_athlete_ai.models.db  # noqa: F401
from hybrid_athlete_ai.database import Base
from hybrid_athlete_ai.mcp import tools as athlete_tools
from hybrid_athlete_ai.schemas.quick import QuickWorkoutCreate
from hybrid_athlete_ai.services import workout_service
from hybrid_athlete_ai.models.enums import SessionType


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


def _seed_strength_history(db):
    for day_offset, weight in [(0, 100), (7, 110), (14, 120)]:
        workout_service.create_quick_workout(
            db,
            QuickWorkoutCreate(
                date=date.today() - timedelta(days=day_offset),
                session_type=SessionType.STRENGTH,
                title=f"Squat day {weight}",
                strength_lines=[f"Back Squat: {weight}x5x1"],
            ),
        )


def test_get_recent_workouts(db_session):
    _seed_strength_history(db_session)
    workouts = athlete_tools.get_recent_workouts(db_session, limit=5)
    assert len(workouts) == 3
    assert workouts[0]["session_type"] == "strength"


def test_get_personal_records_mcp(db_session):
    _seed_strength_history(db_session)
    records = athlete_tools.get_personal_records(db_session, exercise_name="Back Squat")
    assert len(records) == 1
    assert records[0]["weight_kg"] == 120


def test_get_strength_history_mcp(db_session):
    _seed_strength_history(db_session)
    history = athlete_tools.get_strength_history_tool(db_session, exercise_name="Back Squat", weeks=12)
    assert len(history) == 3
    assert history[0]["best_weight_kg"] == 120
    assert history[-1]["best_weight_kg"] == 100


def test_log_workout_quick_mcp(db_session):
    workout = athlete_tools.log_workout_quick(
        db_session,
        workout_date=date.today(),
        session_type="strength",
        title="Press day",
        strength_lines=["Strict Press: 40x5, 50x3, 30x8"],
    )
    assert workout["title"] == "Press day"
    assert workout["exercises"][0]["name"] == "Strict Press"
    assert len(workout["exercises"][0]["sets"]) == 3
