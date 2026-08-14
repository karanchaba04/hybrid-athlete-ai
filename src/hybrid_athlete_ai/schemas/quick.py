from datetime import date

from pydantic import BaseModel, Field

from hybrid_athlete_ai.models.enums import DataSource, SessionType, WodFormat


class QuickWorkoutCreate(BaseModel):
    """Convenient logging — type shorthand instead of nested JSON."""

    date: date
    session_type: SessionType
    title: str
    duration_minutes: int | None = None
    notes: str | None = None
    source: DataSource = DataSource.MANUAL

    # Strength / Olympic / Skills — one exercise per line, multiple sets on same line
    # e.g. "Strict Press: 40x5, 50x3, 30x8" or "Back Squat: 100x5x3"
    strength_lines: list[str] = Field(default_factory=list)

    # Running
    distance_km: float | None = None
    run_duration: str | None = None  # mm:ss or decimal minutes

    # CrossFit / HYROX conditioning WODs
    wod_format: WodFormat | None = None
    wod_description: str | None = None
    wod_score: str | None = None
