from fastapi.testclient import TestClient

from hybrid_athlete_ai.models.enums import CrossFitScoreType, RunningWorkoutType, RxStatus, SessionType


def test_create_running_workout_api(client: TestClient):
    response = client.post(
        "/api/v1/workouts",
        json={
            "date": "2026-08-19",
            "session_type": "running",
            "title": "Threshold",
            "running_metrics": {
                "distance_km": 8.0,
                "duration_seconds": 2472,
                "workout_type": "threshold",
                "average_hr": 168,
            },
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["running_metrics"]["distance_km"] == 8.0
    assert data["running_metrics"]["average_pace_sec_per_km"] == 309.0


def test_rep_records_api(client: TestClient):
    client.post(
        "/api/v1/workouts",
        json={
            "date": "2026-08-19",
            "session_type": "strength",
            "title": "Squat",
            "exercises": [
                {
                    "name": "Back Squat",
                    "sets": [{"set_number": 1, "reps": 5, "weight_kg": 110}],
                }
            ],
        },
    )
    response = client.get(
        "/api/v1/analytics/rep-records",
        params={"movement": "Back Squat", "source": "strength"},
    )
    assert response.status_code == 200
    summary = response.json()
    assert summary["movement"] == "Back Squat"
    assert any(record["rep_count"] == 5 for record in summary["records"])


def test_crossfit_history_api(client: TestClient):
    client.post(
        "/api/v1/workouts",
        json={
            "date": "2026-08-19",
            "session_type": "crossfit",
            "title": "Fran",
            "crossfit_performances": [
                {
                    "workout_name": "Fran",
                    "score_type": "time",
                    "score_seconds": 288,
                    "rx_status": "rx",
                }
            ],
        },
    )
    response = client.get(
        "/api/v1/analytics/crossfit/history",
        params={"workout_name": "Fran", "rx_status": "rx"},
    )
    assert response.status_code == 200
    assert response.json()["entries"][0]["score_seconds"] == 288


def test_backward_compatible_strength_workout(client: TestClient):
    payload = {
        "date": "2026-08-14",
        "session_type": "strength",
        "title": "Lower Body Strength",
        "duration_minutes": 75,
        "source": "manual",
        "exercises": [
            {
                "name": "Back Squat",
                "sets": [
                    {"set_number": 1, "reps": 5, "weight_kg": 80},
                    {"set_number": 2, "reps": 5, "weight_kg": 90},
                    {"set_number": 3, "reps": 5, "weight_kg": 100},
                ],
            }
        ],
    }
    create_response = client.post("/api/v1/workouts", json=payload)
    assert create_response.status_code == 201

    pr_response = client.get("/api/v1/analytics/prs", params={"exercise_name": "Back Squat"})
    assert pr_response.status_code == 200
    assert pr_response.json()[0]["weight_kg"] == 100
