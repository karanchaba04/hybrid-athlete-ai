from datetime import date

from pydantic import BaseModel, Field

from hybrid_athlete_ai.models.enums import DataSource, SessionType, WodFormat
from hybrid_athlete_ai.models.exercise import ExerciseEntry


class TrainingSession(BaseModel):
    id: int | None = None
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
