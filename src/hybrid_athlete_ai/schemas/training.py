from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from hybrid_athlete_ai.models.enums import DataSource, SessionType, WodFormat
from hybrid_athlete_ai.models.exercise import ExerciseEntry


class TrainingSessionCreate(BaseModel):
    date: date
    session_type: SessionType
    title: str
    duration_minutes: int | None = None
    notes: str | None = None
    source: DataSource = DataSource.MANUAL
    wod_format: WodFormat | None = None
    wod_description: str | None = None
    wod_score: str | None = None
    exercises: list[ExerciseEntry] = Field(default_factory=list)


class TrainingSessionRead(TrainingSessionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None


class PersonalRecord(BaseModel):
    exercise_name: str
    weight_kg: float
    reps: int | None = None
    date: date
    session_id: int
    session_title: str


class WeeklyVolume(BaseModel):
    week_start: date
    week_end: date
    total_volume_kg: float
    session_count: int
    sessions_by_type: dict[str, int]
