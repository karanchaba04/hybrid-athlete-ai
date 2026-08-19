from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hybrid_athlete_ai.database import Base


class RunningMetricsORM(Base):
    __tablename__ = "running_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    average_pace_sec_per_km: Mapped[float | None] = mapped_column(Float)
    average_hr: Mapped[int | None] = mapped_column(Integer)
    max_hr: Mapped[int | None] = mapped_column(Integer)
    training_load: Mapped[float | None] = mapped_column(Float)
    elevation_gain_m: Mapped[float | None] = mapped_column(Float)
    average_cadence: Mapped[int | None] = mapped_column(Integer)
    workout_type: Mapped[str] = mapped_column(String(32), nullable=False, default="other")

    session: Mapped["TrainingSessionORM"] = relationship(back_populates="running_metrics")


class WorkoutDefinitionORM(Base):
    __tablename__ = "workout_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    default_score_type: Mapped[str | None] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    performances: Mapped[list["CrossFitPerformanceORM"]] = relationship(
        back_populates="workout_definition",
    )


class CrossFitPerformanceORM(Base):
    __tablename__ = "crossfit_performances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id"),
        nullable=False,
        index=True,
    )
    workout_definition_id: Mapped[int] = mapped_column(
        ForeignKey("workout_definitions.id"),
        nullable=False,
        index=True,
    )
    score_type: Mapped[str] = mapped_column(String(32), nullable=False)
    score_seconds: Mapped[int | None] = mapped_column(Integer)
    score_reps: Mapped[int | None] = mapped_column(Integer)
    score_rounds: Mapped[int | None] = mapped_column(Integer)
    score_load_kg: Mapped[float | None] = mapped_column(Float)
    score_calories: Mapped[int | None] = mapped_column(Integer)
    score_distance_m: Mapped[float | None] = mapped_column(Float)
    score_points: Mapped[float | None] = mapped_column(Float)
    score_display: Mapped[str | None] = mapped_column(String(64))
    rx_status: Mapped[str] = mapped_column(String(16), nullable=False, default="rx")
    time_cap_seconds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped["TrainingSessionORM"] = relationship(back_populates="crossfit_performances")
    workout_definition: Mapped["WorkoutDefinitionORM"] = relationship(back_populates="performances")


class LiftPerformanceORM(Base):
    __tablename__ = "lift_performances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movement: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    successful: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("training_sessions.id"), index=True)
    exercise_set_id: Mapped[int | None] = mapped_column(
        ForeignKey("exercise_sets.id"),
        nullable=True,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped["TrainingSessionORM | None"] = relationship(back_populates="lift_performances")
    exercise_set: Mapped["ExerciseSetORM | None"] = relationship(back_populates="lift_performance")
