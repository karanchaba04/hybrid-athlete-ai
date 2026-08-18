from anthropic import APIError, APIStatusError
from fastapi import APIRouter, HTTPException

from hybrid_athlete_ai.agents.accessory_graph import recommend_accessory_workouts, reset_accessory_graph
from hybrid_athlete_ai.agents.coach_graph import reset_coach_graph
from hybrid_athlete_ai.agents.runner import chat
from hybrid_athlete_ai.database import SessionLocal
from hybrid_athlete_ai.schemas.coach import (
    AccessoryPlanRequest,
    AccessoryPlanResponse,
    CoachChatRequest,
    CoachChatResponse,
)
from hybrid_athlete_ai.services.accessory_context import build_accessory_context

router = APIRouter(prefix="/coach", tags=["coach"])


def _coach_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, APIStatusError):
        detail = f"Anthropic API error ({exc.status_code}): {exc.message}"
        if exc.status_code == 404:
            detail += " Check COACH_MODEL in .env matches a model your API key supports."
        return HTTPException(status_code=502, detail=detail)
    if isinstance(exc, APIError):
        return HTTPException(status_code=502, detail=f"Anthropic API error: {exc}")
    return HTTPException(status_code=500, detail=f"Coach error: {exc}")


@router.post("/chat", response_model=CoachChatResponse)
def coach_chat(payload: CoachChatRequest):
    reset_coach_graph()
    try:
        response = chat(payload.message, thread_id=payload.thread_id)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (APIError, APIStatusError) as exc:
        raise _coach_http_error(exc) from exc
    except Exception as exc:
        raise _coach_http_error(exc) from exc

    return CoachChatResponse(response=response, thread_id=payload.thread_id)


@router.post("/accessories", response_model=AccessoryPlanResponse)
def recommend_accessories(payload: AccessoryPlanRequest):
    reset_accessory_graph()
    db = SessionLocal()
    try:
        context_summary = build_accessory_context(db)
    finally:
        db.close()

    try:
        recommendation = recommend_accessory_workouts(
            available_slots=payload.available_slots,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (APIError, APIStatusError) as exc:
        raise _coach_http_error(exc) from exc
    except Exception as exc:
        raise _coach_http_error(exc) from exc

    return AccessoryPlanResponse(
        recommendation=recommendation,
        context_summary=context_summary,
    )
