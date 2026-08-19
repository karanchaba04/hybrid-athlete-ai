from pydantic import BaseModel, ConfigDict

from hybrid_athlete_ai.models.enums import SetType


class ExerciseSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    set_number: int
    reps: int | None = None
    weight_kg: float | None = None
    duration_seconds: int | None = None
    distance_meters: float | None = None
    rpe: float | None = None
    set_type: SetType = SetType.NORMAL
    successful: bool = True


class ExerciseEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    sets: list[ExerciseSet]
    notes: str | None = None
