from sqlalchemy import create_engine, inspect, text

from hybrid_athlete_ai.database import _migrate_training_sessions


def test_migrate_training_sessions_adds_missing_wod_columns():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE training_sessions (
                    id INTEGER PRIMARY KEY,
                    date DATE NOT NULL,
                    session_type VARCHAR(32) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    duration_minutes INTEGER,
                    notes TEXT,
                    source VARCHAR(32) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
                """
            )
        )

    _migrate_training_sessions(engine)

    columns = {col["name"] for col in inspect(engine).get_columns("training_sessions")}
    assert {"wod_format", "wod_description", "wod_score"}.issubset(columns)
