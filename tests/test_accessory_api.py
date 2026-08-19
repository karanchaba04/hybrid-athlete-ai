from unittest.mock import patch

from hybrid_athlete_ai.schemas.coach import (
    AccessoryExercise,
    AccessoryRecommendation,
    AccessorySlotPlan,
)
from hybrid_athlete_ai.services.coach_persistence import compute_context_hash


def test_recommend_accessories_endpoint(client):
    mock_recommendation = AccessoryRecommendation(
        slots=[
            AccessorySlotPlan(
                slot="Tue 30 min",
                exercises=[
                    AccessoryExercise(
                        name="Strict Press",
                        prescription="4×5 @ RPE 7",
                    ),
                ],
            ),
        ],
        rationale="Press volume is low this week while squat load is already high.",
        warnings=["SugarWOD programming not available — used logged sessions only."],
    )

    with patch(
        "hybrid_athlete_ai.api.coach_routes.recommend_accessory_workouts",
        return_value=mock_recommendation,
    ) as mock_generate:
        response = client.post(
            "/api/v1/coach/accessories",
            json={
                "available_slots": ["Tue 30 min", "Thu 45 min"],
                "notes": "Shoulder feels tight",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendation"]["slots"][0]["slot"] == "Tue 30 min"
    assert "weekly_volume" in body["context_summary"]
    assert body["recommendation"]["rationale"]
    assert body["from_cache"] is False
    assert body["plan_id"] is not None
    mock_generate.assert_called_once()

    cached = client.post(
        "/api/v1/coach/accessories",
        json={
            "available_slots": ["Tue 30 min", "Thu 45 min"],
            "notes": "Shoulder feels tight",
        },
    )
    assert cached.status_code == 200
    assert cached.json()["from_cache"] is True
    mock_generate.assert_called_once()


def test_recommend_accessories_force_regenerate(client):
    mock_recommendation = AccessoryRecommendation(
        slots=[
            AccessorySlotPlan(
                slot="Tue 30 min",
                exercises=[AccessoryExercise(name="Row", prescription="3×10")],
            ),
        ],
        rationale="Updated plan",
        warnings=[],
    )

    with patch(
        "hybrid_athlete_ai.api.coach_routes.recommend_accessory_workouts",
        return_value=mock_recommendation,
    ) as mock_generate:
        client.post(
            "/api/v1/coach/accessories",
            json={"available_slots": ["Tue 30 min"]},
        )
        response = client.post(
            "/api/v1/coach/accessories",
            json={"available_slots": ["Tue 30 min"], "force_regenerate": True},
        )

    assert response.status_code == 200
    assert response.json()["from_cache"] is False
    assert mock_generate.call_count == 2


def test_recommend_accessories_requires_slots(client):
    response = client.post("/api/v1/coach/accessories", json={"available_slots": []})
    assert response.status_code == 422


def test_list_coach_plans(client):
    mock_recommendation = AccessoryRecommendation(
        slots=[
            AccessorySlotPlan(
                slot="Sat 30 min",
                exercises=[AccessoryExercise(name="Pull-ups", prescription="3×8")],
            ),
        ],
        rationale="Pull balance",
        warnings=[],
    )

    with patch(
        "hybrid_athlete_ai.api.coach_routes.recommend_accessory_workouts",
        return_value=mock_recommendation,
    ):
        client.post(
            "/api/v1/coach/accessories",
            json={"available_slots": ["Sat 30 min"]},
        )

    response = client.get("/api/v1/coach/plans", params={"plan_type": "accessory"})
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) >= 1
    assert plans[0]["plan_type"] == "accessory"


def test_context_hash_changes_with_training_context():
    base = {"week_start": "2026-08-18", "active_goals": [{"id": 1}]}
    changed = {"week_start": "2026-08-18", "active_goals": [{"id": 1}, {"id": 2}]}
    slots = ["Tue 30 min"]

    hash_a = compute_context_hash(base, available_slots=slots, notes=None)
    hash_b = compute_context_hash(changed, available_slots=slots, notes=None)
    assert hash_a != hash_b
