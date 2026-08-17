from anthropic import APIError, APIStatusError
from fastapi import APIRouter, HTTPException

from hybrid_athlete_ai.agents.coach_graph import reset_coach_graph
from hybrid_athlete_ai.agents.runner import chat
from hybrid_athlete_ai.schemas.coach import CoachChatRequest, CoachChatResponse

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
