from unittest.mock import patch

from hybrid_athlete_ai.schemas.coach import (
    AccessoryExercise,
    AccessoryRecommendation,
    AccessorySlotPlan,
)


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
    ):
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


def test_recommend_accessories_requires_slots(client):
    response = client.post("/api/v1/coach/accessories", json={"available_slots": []})
    assert response.status_code == 422
