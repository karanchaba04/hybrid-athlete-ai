from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from hybrid_athlete_ai.models.enums import (
    CrossFitScoreType,
    DataSource,
    RunningWorkoutType,
    RxStatus,
    SessionType,
    WodFormat,
)
from hybrid_athlete_ai.models.exercise import ExerciseEntry


class RunningMetricsCreate(BaseModel):
    distance_km: float
    duration_seconds: int
    average_pace_sec_per_km: float | None = None
    average_hr: int | None = None
    max_hr: int | None = None
    training_load: float | None = None
    elevation_gain_m: float | None = None
    average_cadence: int | None = None
    workout_type: RunningWorkoutType = RunningWorkoutType.OTHER


class RunningMetricsRead(RunningMetricsCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int


class CrossFitPerformanceCreate(BaseModel):
    workout_name: str
    workout_description: str | None = None
    score_type: CrossFitScoreType
    score_seconds: int | None = None
    score_reps: int | None = None
    score_rounds: int | None = None
    score_load_kg: float | None = None
    score_calories: int | None = None
    score_distance_m: float | None = None
    score_points: float | None = None
    score_display: str | None = None
    rx_status: RxStatus = RxStatus.RX
    time_cap_seconds: int | None = None
    notes: str | None = None


class CrossFitPerformanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    workout_definition_id: int
    workout_name: str
    workout_description: str | None = None
    score_type: CrossFitScoreType
    score_seconds: int | None = None
    score_reps: int | None = None
    score_rounds: int | None = None
    score_load_kg: float | None = None
    score_calories: int | None = None
    score_distance_m: float | None = None
    score_points: float | None = None
    score_display: str | None = None
    rx_status: RxStatus
    time_cap_seconds: int | None = None
    notes: str | None = None
    created_at: datetime | None = None


class LiftPerformanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movement: str
    weight_kg: float
    reps: int
    successful: bool
    date: date
    session_id: int | None = None
    exercise_set_id: int | None = None
    notes: str | None = None


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
    running_metrics: RunningMetricsCreate | None = None
    crossfit_performances: list[CrossFitPerformanceCreate] = Field(default_factory=list)


class TrainingSessionRead(TrainingSessionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
    running_metrics: RunningMetricsRead | None = None
    crossfit_performances: list[CrossFitPerformanceRead] = Field(default_factory=list)


class PersonalRecord(BaseModel):
    exercise_name: str
    weight_kg: float
    reps: int | None = None
    date: date
    session_id: int
    session_title: str


class RepRecord(BaseModel):
    """Rep-based personal record for a movement/exercise at a specific rep count."""

    movement: str
    rep_count: int
    weight_kg: float
    is_estimated: bool
    date: date
    session_id: int | None = None
    session_title: str | None = None
    previous_weight_kg: float | None = None
    improvement_kg: float | None = None


class RepRecordSummary(BaseModel):
    movement: str
    records: list[RepRecord]
    heaviest_successful_set_kg: float | None = None
    estimated_1rm_kg: float | None = None
    recent_history: list[RepRecord] = Field(default_factory=list)


class WeeklyVolume(BaseModel):
    week_start: date
    week_end: date
    total_volume_kg: float
    session_count: int
    sessions_by_type: dict[str, int]


class RunningHistoryEntry(BaseModel):
    date: date
    session_id: int
    session_title: str
    distance_km: float
    duration_seconds: int
    average_pace_sec_per_km: float | None = None
    average_hr: int | None = None
    max_hr: int | None = None
    training_load: float | None = None
    elevation_gain_m: float | None = None
    average_cadence: int | None = None
    workout_type: RunningWorkoutType


class WorkoutDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    default_score_type: CrossFitScoreType | None = None


class CrossFitHistoryEntry(BaseModel):
    date: date
    session_id: int
    performance_id: int
    workout_name: str
    score_type: CrossFitScoreType
    score_seconds: int | None = None
    score_reps: int | None = None
    score_rounds: int | None = None
    score_load_kg: float | None = None
    score_calories: int | None = None
    score_distance_m: float | None = None
    score_points: float | None = None
    score_display: str | None = None
    rx_status: RxStatus
    delta_from_previous: float | None = None
    delta_from_first: float | None = None
    delta_display: str | None = None


class CrossFitHistorySummary(BaseModel):
    workout_name: str
    rx_status: RxStatus
    score_type: CrossFitScoreType
    entries: list[CrossFitHistoryEntry]
