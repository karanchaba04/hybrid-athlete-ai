from datetime import date
from src.models.training import SessionType, DataSource, TrainingSession

run = TrainingSession(
    date=date.today(),
    session_type=SessionType.RUNNING,
    title="30 mins threshold run",
    duration_minutes=30,
    notes="Felt strong. Average HR around threshold",
    source=DataSource.GARMIN
)


hyrox = TrainingSession(
    date=date.today(),
    session_type=SessionType.HYROX,
    title="HYROX Simulation",
    duration_minutes=76,
    source=DataSource.ROXFIT,
)

crossfit = TrainingSession(
    date=date.today(),
    session_type=SessionType.CROSSFIT,
    title="CrossFit Class",
    duration_minutes=60,
    source=DataSource.SUGARWOD,
)

print(run.model_dump())
print(hyrox.model_dump())
print(crossfit.model_dump())