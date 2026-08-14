from hybrid_athlete_ai.models.exercise import ExerciseEntry, ExerciseSet

from hybrid_athlete_ai.services.training_analytics import (
    calculate_total_reps,
    calculate_volume,
    get_heaviest_set,
)

def test_calculate_volume():
    exercise = ExerciseEntry(
        name="Back Squat",
        sets=[
            ExerciseSet(
                set_number=1,
                reps=5,
                weight_kg=80,
            ),
            ExerciseSet(
                set_number=2,
                reps=5,
                weight_kg=90,
            ),
            ExerciseSet(
                set_number=3,
                reps=5,
                weight_kg=100,
            ),
        ],
    )

    assert calculate_volume(exercise) == 1350


def test_total_reps():
    exercise = ExerciseEntry(
        name="Pull-Up",
        sets=[
            ExerciseSet(set_number=1, reps=10),
            ExerciseSet(set_number=2, reps=8),
        ],
    )

    assert calculate_total_reps(exercise) == 18


def test_heaviest_set():
    exercise = ExerciseEntry(
        name="Back Squat",
        sets=[
            ExerciseSet(set_number=1, reps=5, weight_kg=80),
            ExerciseSet(set_number=2, reps=3, weight_kg=100),
        ],
    )

    heaviest = get_heaviest_set(exercise)

    assert heaviest is not None
    assert heaviest.weight_kg == 100