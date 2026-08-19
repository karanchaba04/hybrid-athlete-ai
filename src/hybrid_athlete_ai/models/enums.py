from enum import StrEnum


class SessionType(StrEnum):
    STRENGTH = "strength"
    RUNNING = "running"
    CROSSFIT = "crossfit"
    HYROX = "hyrox"
    OLYMPIC_LIFTING = "olympic_lifting"
    SKILLS = "skills"
    RECOVERY = "recovery"
    OTHER = "other"


class DataSource(StrEnum):
    MANUAL = "manual"
    SUGARWOD = "sugarwod"
    GARMIN = "garmin"
    STRAVA = "strava"
    ROXFIT = "roxfit"
    GOOGLE_SHEETS = "google_sheets"


class SetType(StrEnum):
    NORMAL = "normal"
    WARMUP = "warmup"
    DROP = "drop"
    AMRAP = "amrap"
    EMOM = "emom"
    HOLD = "hold"


class WodFormat(StrEnum):
    AMRAP = "amrap"
    EMOM = "emom"
    FOR_TIME = "for_time"
    CHIPPER = "chipper"
    TABATA = "tabata"
    INTERVALS = "intervals"
    OTHER = "other"


class RunningWorkoutType(StrEnum):
    EASY = "easy"
    ZONE2 = "zone2"
    RECOVERY = "recovery"
    LONG_RUN = "long_run"
    TEMPO = "tempo"
    THRESHOLD = "threshold"
    INTERVALS = "intervals"
    RACE = "race"
    OTHER = "other"


class CrossFitScoreType(StrEnum):
    TIME = "time"
    ROUNDS_REPS = "rounds_reps"
    REPS = "reps"
    LOAD = "load"
    CALORIES = "calories"
    DISTANCE = "distance"
    POINTS = "points"


class RxStatus(StrEnum):
    RX = "rx"
    SCALED = "scaled"


class CoachPlanType(StrEnum):
    ACCESSORY = "accessory"
    WEEKLY_REVIEW = "weekly_review"
    COACH_TIP = "coach_tip"


class CoachPlanStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"
