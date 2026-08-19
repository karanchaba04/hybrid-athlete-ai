from datetime import date


def test_quick_strength_log(client):
    payload = {
        "date": date.today().isoformat(),
        "session_type": "strength",
        "title": "Upper Body",
        "strength_lines": [
            "Strict Press: 40x5, 50x3, 30x8",
            "Back Squat: 100x5x3",
        ],
    }

    response = client.post("/api/v1/workouts/quick", json=payload)
    assert response.status_code == 201
    body = response.json()

    assert len(body["exercises"]) == 2
    strict_press = body["exercises"][0]
    assert strict_press["name"] == "Strict Press"
    assert len(strict_press["sets"]) == 3
    assert strict_press["sets"][1]["weight_kg"] == 50


def test_quick_running_log(client):
    payload = {
        "date": date.today().isoformat(),
        "session_type": "running",
        "title": "Easy 5K",
        "distance_km": 5.0,
        "run_duration": "24:30",
    }

    response = client.post("/api/v1/workouts/quick", json=payload)
    assert response.status_code == 201
    body = response.json()

    metrics = body["running_metrics"]
    assert metrics is not None
    assert metrics["distance_km"] == 5.0
    assert metrics["duration_seconds"] == 1470
    assert body["exercises"] == []


def test_quick_wod_log(client):
    payload = {
        "date": date.today().isoformat(),
        "session_type": "crossfit",
        "title": "Friday Conditioning",
        "duration_minutes": 20,
        "wod_format": "amrap",
        "wod_description": "20 min AMRAP: 10 burpees, 15 wall balls, 200m run",
        "wod_score": "8+12",
    }

    response = client.post("/api/v1/workouts/quick", json=payload)
    assert response.status_code == 201
    body = response.json()

    assert body["wod_format"] == "amrap"
    assert body["wod_score"] == "8+12"
    assert "burpees" in body["wod_description"]
