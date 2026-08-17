from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hybrid_athlete_ai.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_training_sessions(db_engine=engine) -> None:
    """Add columns introduced after initial V1 schema (SQLite create_all does not alter tables)."""
    inspector = inspect(db_engine)
    if "training_sessions" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("training_sessions")}
    additions = {
        "wod_format": "VARCHAR(32)",
        "wod_description": "TEXT",
        "wod_score": "VARCHAR(64)",
    }

    with db_engine.begin() as connection:
        for column_name, column_type in additions.items():
            if column_name not in existing:
                connection.execute(
                    text(f"ALTER TABLE training_sessions ADD COLUMN {column_name} {column_type}")
                )


def init_db() -> None:
    # Import ORM models so metadata is registered before create_all.
    import hybrid_athlete_ai.models.db  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_training_sessions()
