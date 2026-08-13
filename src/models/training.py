from datetime import date
from enum import Enum
from pydantic import BaseModel


class SessionType(str, Enum): # means the value is constrained to one of my allowed session types
    STRENGTH = "strength"
    RUNNING = "running"
    CROSSFIT = "crossfit"
    HYROX = "hyrox"
    ACCESSORY = "accessory"
    MOBILITY = "mobility"
    OTHER = "other"


class DataSource(str, Enum):
    MANUAL = "manual"
    SUGARWOD = "sugarwod"
    GARMIN = "garmin"
    STRAVA = "strava"
    ROXFIT = "roxfit"
    GOOGLE_SHEETS = "google_sheets"



class TrainingSession(BaseModel):
    id: int | None = None
    date: date
    session_type: SessionType
    title: str
    duration_minutes: int | None = None
    notes: str | None = None
    source: DataSource = DataSource.MANUAL

