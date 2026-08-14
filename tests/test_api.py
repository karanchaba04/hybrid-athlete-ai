from datetime import date

from hybrid_athlete_ai.models.exercise import ExerciseEntry, ExerciseSet


def test_create_and_list_workout(client):
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
    created = create_response.json()
    assert created["title"] == "Lower Body Strength"
    assert created["exercises"][0]["name"] == "Back Squat"

    list_response = client.get("/api/v1/workouts")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_personal_records(client):
    payload = {
        "date": "2026-08-14",
        "session_type": "strength",
        "title": "Squat Day",
        "exercises": [
            {
                "name": "Back Squat",
                "sets": [{"set_number": 1, "reps": 3, "weight_kg": 120}],
            }
        ],
    }
    client.post("/api/v1/workouts", json=payload)

    response = client.get("/api/v1/analytics/prs", params={"exercise_name": "Back Squat"})
    assert response.status_code == 200
    records = response.json()
    assert len(records) == 1
    assert records[0]["weight_kg"] == 120


def test_weekly_volume(client):
    payload = {
        "date": date.today().isoformat(),
        "session_type": "strength",
        "title": "Volume Day",
        "exercises": [
            {
                "name": "Back Squat",
                "sets": [
                    {"set_number": 1, "reps": 5, "weight_kg": 100},
                    {"set_number": 2, "reps": 5, "weight_kg": 100},
                ],
            }
        ],
    }
    client.post("/api/v1/workouts", json=payload)

    response = client.get("/api/v1/analytics/weekly-volume")
    assert response.status_code == 200
    volume = response.json()
    assert volume["total_volume_kg"] == 1000
    assert volume["session_count"] == 1


def test_goals(client):
    create_response = client.post(
        "/api/v1/goals",
        json={
            "category": "strength",
            "title": "140kg back squat",
            "target_value": 140,
            "target_unit": "kg",
            "exercise_name": "Back Squat",
        },
    )
    assert create_response.status_code == 201
    goal_id = create_response.json()["id"]

    list_response = client.get("/api/v1/goals")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"status": "achieved"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "achieved"
