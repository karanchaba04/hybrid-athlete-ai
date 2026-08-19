from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hybrid_athlete_ai.database import Base
from hybrid_athlete_ai.models.enums import CoachPlanStatus, CoachPlanType


class CoachPlanORM(Base):
    __tablename__ = "coach_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    plan_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    context_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    recommendation_json: Mapped[str] = mapped_column(Text, nullable=False)
    context_summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    request_json: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=CoachPlanStatus.ACTIVE.value,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CoachThreadORM(Base):
    __tablename__ = "coach_threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255))
    week_start: Mapped[date | None] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    messages: Mapped[list["CoachMessageORM"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="CoachMessageORM.created_at",
    )


class CoachMessageORM(Base):
    __tablename__ = "coach_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("coach_threads.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    thread: Mapped[CoachThreadORM] = relationship(back_populates="messages")
