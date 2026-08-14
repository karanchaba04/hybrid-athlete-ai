from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hybrid_athlete_ai.database import Base
from hybrid_athlete_ai.models.enums import DataSource, SetType


class GoalCategory(str, Enum):
    STRENGTH = "strength"
    RUNNING = "running"
    GYMNASTICS = "gymnastics"
    HYROX = "hyrox"
    BODY_COMPOSITION = "body_composition"
    HABIT = "habit"
    OTHER = "other"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    ABANDONED = "abandoned"


class TrainingSessionORM(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    session_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default=DataSource.MANUAL.value)
    wod_format: Mapped[str | None] = mapped_column(String(32))
    wod_description: Mapped[str | None] = mapped_column(Text)
    wod_score: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    exercises: Mapped[list["ExerciseEntryORM"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ExerciseEntryORM.id",
    )


class ExerciseEntryORM(Base):
    __tablename__ = "exercise_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    session: Mapped[TrainingSessionORM] = relationship(back_populates="exercises")
    sets: Mapped[list["ExerciseSetORM"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="ExerciseSetORM.set_number",
    )


class ExerciseSetORM(Base):
    __tablename__ = "exercise_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise_entries.id"), nullable=False)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    distance_meters: Mapped[float | None] = mapped_column(Float)
    rpe: Mapped[float | None] = mapped_column(Float)
    set_type: Mapped[str] = mapped_column(String(32), nullable=False, default=SetType.NORMAL.value)

    exercise: Mapped[ExerciseEntryORM] = relationship(back_populates="sets")


class GoalORM(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_value: Mapped[float | None] = mapped_column(Float)
    target_unit: Mapped[str | None] = mapped_column(String(32))
    exercise_name: Mapped[str | None] = mapped_column(String(255), index=True)
    deadline: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=GoalStatus.ACTIVE.value)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
