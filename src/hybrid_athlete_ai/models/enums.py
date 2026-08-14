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
