import re

from hybrid_athlete_ai.models.exercise import ExerciseEntry, ExerciseSet
from hybrid_athlete_ai.models.enums import SetType

# weight x reps  OR  weight x reps x set_count (e.g. 100x5x3 = 3 sets of 5 at 100kg)
_SET_PATTERN = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*x\s*(\d+)\s*(?:x\s*(\d+))?\s*$",
    re.IGNORECASE,
)


def parse_strength_line(line: str) -> ExerciseEntry:
    """
    Parse a single strength line into one exercise with multiple sets.

    Examples:
        "Strict Press: 40x5, 50x3, 30x8"
        "Back Squat: 100x5x3"
        "Bench Press 60x5, 60x5, 60x5"
    """
    line = line.strip()
    if not line:
        raise ValueError("Empty strength line")

    if ":" in line:
        name, sets_part = line.split(":", 1)
        name = name.strip()
        sets_part = sets_part.strip()
    else:
        # Last token group starting with digit is sets; everything before is exercise name
        match = re.search(r"\s+(\d+(?:\.\d+)?\s*x\s*\d+.*)$", line, re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not parse strength line: {line}")
        name = line[: match.start()].strip()
        sets_part = match.group(1).strip()

    if not name:
        raise ValueError(f"Missing exercise name in: {line}")

    set_tokens = [token.strip() for token in sets_part.split(",") if token.strip()]
    if not set_tokens:
        raise ValueError(f"No sets found for {name}")

    sets: list[ExerciseSet] = []
    set_number = 1

    for token in set_tokens:
        match = _SET_PATTERN.match(token)
        if not match:
            raise ValueError(f"Invalid set format '{token}' in line: {line}")

        weight_kg = float(match.group(1))
        reps = int(match.group(2))
        repeat = int(match.group(3)) if match.group(3) else 1

        for _ in range(repeat):
            sets.append(
                ExerciseSet(
                    set_number=set_number,
                    reps=reps,
                    weight_kg=weight_kg,
                    set_type=SetType.NORMAL,
                )
            )
            set_number += 1

    return ExerciseEntry(name=name, sets=sets)


def parse_strength_lines(lines: list[str]) -> list[ExerciseEntry]:
    return [parse_strength_line(line) for line in lines if line.strip()]


def parse_run_duration(duration: str) -> int:
    """Parse run duration to seconds. Accepts '24:30', '1:05:00', or '45' (minutes)."""
    duration = duration.strip()
    if ":" in duration:
        parts = [int(p) for p in duration.split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        raise ValueError(f"Invalid duration format: {duration}")

    # Decimal minutes
    minutes = float(duration)
    return int(minutes * 60)
