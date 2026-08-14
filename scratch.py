"""Quick manual demo script — log a workout via the domain models."""

from datetime import date

from hybrid_athlete_ai.models.exercise import ExerciseEntry, ExerciseSet
from hybrid_athlete_ai.models.training import DataSource, SessionType, TrainingSession

session = TrainingSession(
    date=date.today(),
    session_type=SessionType.STRENGTH,
    title="Lower Body Strength",
    duration_minutes=75,
    source=DataSource.MANUAL,
    exercises=[
        ExerciseEntry(
            name="Back Squat",
            sets=[
                ExerciseSet(set_number=1, reps=5, weight_kg=80),
                ExerciseSet(set_number=2, reps=5, weight_kg=90),
                ExerciseSet(set_number=3, reps=5, weight_kg=100),
            ],
        ),
        ExerciseEntry(
            name="Weighted Pull-Up",
            sets=[
                ExerciseSet(set_number=1, reps=5, weight_kg=20),
                ExerciseSet(set_number=2, reps=3, weight_kg=30),
            ],
        ),
    ],
)

if __name__ == "__main__":
    print(session.model_dump_json(indent=2))
