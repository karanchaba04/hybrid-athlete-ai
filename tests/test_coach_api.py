from unittest.mock import patch

import pytest

from hybrid_athlete_ai.agents.coach_graph import reset_coach_graph
from hybrid_athlete_ai.agents.tools import COACH_TOOLS
from hybrid_athlete_ai.config import settings


def test_coach_tools_registered():
    tool_names = {tool.name for tool in COACH_TOOLS}
    assert tool_names == {
        "get_recent_workouts",
        "get_workout",
        "get_personal_records",
        "get_weekly_volume",
        "get_current_goals",
        "get_strength_history",
        "log_workout_quick",
    }


def test_coach_chat_without_api_key(client):
    reset_coach_graph()
    original_key = settings.anthropic_api_key
    settings.anthropic_api_key = None
    try:
        response = client.post(
            "/api/v1/coach/chat",
            json={"message": "What is my back squat PR?"},
        )
        assert response.status_code == 503
        assert "ANTHROPIC_API_KEY" in response.json()["detail"]
    finally:
        settings.anthropic_api_key = original_key
        reset_coach_graph()


def test_coach_chat_success(client):
    with patch(
        "hybrid_athlete_ai.api.coach_routes.chat",
        return_value="Your back squat PR is 120 kg.",
    ):
        response = client.post(
            "/api/v1/coach/chat",
            json={"message": "What is my back squat PR?", "thread_id": "test-thread"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Your back squat PR is 120 kg."
    assert body["thread_id"] == "test-thread"


def test_coach_chat_requires_message(client):
    response = client.post("/api/v1/coach/chat", json={"message": ""})
    assert response.status_code == 422
