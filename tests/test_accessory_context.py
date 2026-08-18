from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import hybrid_athlete_ai.models.db  # noqa: F401
from hybrid_athlete_ai.database import Base
from hybrid_athlete_ai.models.enums import SessionType
from hybrid_athlete_ai.models.goal import GoalCreate
from hybrid_athlete_ai.schemas.quick import QuickWorkoutCreate
from hybrid_athlete_ai.services import workout_service
from hybrid_athlete_ai.services.accessory_context import build_accessory_context


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


def test_build_accessory_context_includes_goals_and_load_signals(db_session):
    workout_service.create_goal(
        db_session,
        GoalCreate(
            category="strength",
            title="140kg back squat",
            target_value=140,
            target_unit="kg",
            exercise_name="Back Squat",
        ),
    )
    workout_service.create_quick_workout(
        db_session,
        QuickWorkoutCreate(
            date=date.today(),
            session_type=SessionType.STRENGTH,
            title="Squat emphasis",
            strength_lines=["Back Squat: 100x5x3"],
        ),
    )

    context = build_accessory_context(db_session)

    assert len(context["active_goals"]) == 1
    assert context["load_signals"]["squat_pattern_sessions_this_week"] >= 1
    assert "weekly_volume" in context
    assert "Back Squat" in context["strength_snapshots"]
