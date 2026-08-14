import pytest

from hybrid_athlete_ai.services.quick_log import parse_run_duration, parse_strength_line, parse_strength_lines


def test_parse_varying_sets_same_exercise():
    exercise = parse_strength_line("Strict Press: 40x5, 50x3, 30x8")

    assert exercise.name == "Strict Press"
    assert len(exercise.sets) == 3
    assert exercise.sets[0].weight_kg == 40
    assert exercise.sets[0].reps == 5
    assert exercise.sets[1].weight_kg == 50
    assert exercise.sets[1].reps == 3
    assert exercise.sets[2].weight_kg == 30
    assert exercise.sets[2].reps == 8


def test_parse_repeated_sets_notation():
    exercise = parse_strength_line("Back Squat: 100x5x3")

    assert exercise.name == "Back Squat"
    assert len(exercise.sets) == 3
    assert all(exercise_set.weight_kg == 100 and exercise_set.reps == 5 for exercise_set in exercise.sets)


def test_parse_multiple_exercises():
    exercises = parse_strength_lines(
        [
            "Strict Press: 40x5, 50x3, 30x8",
            "Back Squat: 100x5x3",
        ]
    )

    assert len(exercises) == 2
    assert exercises[0].name == "Strict Press"
    assert exercises[1].name == "Back Squat"


def test_parse_run_duration():
    assert parse_run_duration("24:30") == 1470
    assert parse_run_duration("45") == 2700


def test_invalid_strength_line():
    with pytest.raises(ValueError):
        parse_strength_line("Not a lift")
