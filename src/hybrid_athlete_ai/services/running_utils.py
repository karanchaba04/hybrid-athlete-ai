"""Shared pace helpers for running metrics."""

def derive_pace_sec_per_km(distance_km: float, duration_seconds: int) -> float | None:
    if distance_km <= 0 or duration_seconds <= 0:
        return None
    return duration_seconds / distance_km


def format_pace(pace_sec_per_km: float) -> str:
    total_seconds = int(round(pace_sec_per_km))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}/km"
