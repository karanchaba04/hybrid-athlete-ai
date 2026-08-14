from hybrid_athlete_ai.models.exercise import ExerciseEntry


def calculate_volume(exercise: ExerciseEntry) -> float:
    """Total training volume: sum(reps × weight) for all weighted sets."""
    total_volume = 0.0

    for exercise_set in exercise.sets:
        if exercise_set.reps is not None and exercise_set.weight_kg is not None:
            total_volume += exercise_set.reps * exercise_set.weight_kg

    return total_volume


def get_heaviest_set(exercise: ExerciseEntry):
    weighted_sets = [
        exercise_set
        for exercise_set in exercise.sets
        if exercise_set.weight_kg is not None
    ]

    if not weighted_sets:
        return None

    return max(weighted_sets, key=lambda exercise_set: exercise_set.weight_kg)


def calculate_total_reps(exercise: ExerciseEntry) -> int:
    return sum(exercise_set.reps or 0 for exercise_set in exercise.sets)
