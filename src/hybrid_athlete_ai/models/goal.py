from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


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


class GoalBase(BaseModel):
    category: GoalCategory
    title: str
    target_value: float | None = None
    target_unit: str | None = None
    exercise_name: str | None = None
    deadline: date | None = None
    status: GoalStatus = GoalStatus.ACTIVE
    notes: str | None = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    category: GoalCategory | None = None
    title: str | None = None
    target_value: float | None = None
    target_unit: str | None = None
    exercise_name: str | None = None
    deadline: date | None = None
    status: GoalStatus | None = None
    notes: str | None = None


class Goal(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
