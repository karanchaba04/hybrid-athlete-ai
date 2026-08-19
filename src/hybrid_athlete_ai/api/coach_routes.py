from datetime import date

from anthropic import APIError, APIStatusError
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hybrid_athlete_ai.agents.accessory_graph import recommend_accessory_workouts, reset_accessory_graph
from hybrid_athlete_ai.agents.coach_graph import reset_coach_graph
from hybrid_athlete_ai.agents.runner import chat
from hybrid_athlete_ai.database import get_db
from hybrid_athlete_ai.models.enums import CoachPlanStatus, CoachPlanType
from hybrid_athlete_ai.schemas.coach import (
    AccessoryPlanRequest,
    AccessoryPlanResponse,
    CoachChatRequest,
    CoachChatResponse,
    CoachMessageRead,
    CoachPlanRead,
)
from hybrid_athlete_ai.services.accessory_context import build_accessory_context
from hybrid_athlete_ai.services.coach_persistence import (
    compute_context_hash,
    find_active_plan,
    get_coach_plan,
    get_thread_messages,
    list_coach_plans,
    plan_to_read,
    save_coach_plan,
)

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
def coach_chat(payload: CoachChatRequest, db: Session = Depends(get_db)):
    reset_coach_graph()
    try:
        response = chat(payload.message, thread_id=payload.thread_id, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (APIError, APIStatusError) as exc:
        raise _coach_http_error(exc) from exc
    except Exception as exc:
        raise _coach_http_error(exc) from exc

    return CoachChatResponse(response=response, thread_id=payload.thread_id)


@router.get("/threads/{thread_id}/messages", response_model=list[CoachMessageRead])
def get_chat_messages(thread_id: str, db: Session = Depends(get_db)):
    return get_thread_messages(db, thread_id)


@router.post("/accessories", response_model=AccessoryPlanResponse)
def recommend_accessories(payload: AccessoryPlanRequest, db: Session = Depends(get_db)):
    reset_accessory_graph()
    context_summary = build_accessory_context(db)
    week_start = date.fromisoformat(context_summary["week_start"])
    context_hash = compute_context_hash(
        context_summary,
        available_slots=payload.available_slots,
        notes=payload.notes,
    )

    if not payload.force_regenerate:
        existing = find_active_plan(
            db,
            week_start=week_start,
            plan_type=CoachPlanType.ACCESSORY,
            context_hash=context_hash,
        )
        if existing is not None:
            saved = plan_to_read(existing)
            return AccessoryPlanResponse(
                recommendation=saved.recommendation,
                context_summary=saved.context_summary,
                plan_id=saved.id,
                from_cache=True,
                context_hash=context_hash,
            )

    try:
        recommendation = recommend_accessory_workouts(
            available_slots=payload.available_slots,
            notes=payload.notes,
            context=context_summary,
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (APIError, APIStatusError) as exc:
        raise _coach_http_error(exc) from exc
    except Exception as exc:
        raise _coach_http_error(exc) from exc

    plan = save_coach_plan(
        db,
        week_start=week_start,
        plan_type=CoachPlanType.ACCESSORY,
        context_hash=context_hash,
        recommendation=recommendation,
        context_summary=context_summary,
        request_payload={
            "available_slots": payload.available_slots,
            "notes": payload.notes,
        },
        supersede_existing=True,
    )

    return AccessoryPlanResponse(
        recommendation=recommendation,
        context_summary=context_summary,
        plan_id=plan.id,
        from_cache=False,
        context_hash=context_hash,
    )


@router.get("/plans", response_model=list[CoachPlanRead])
def list_plans(
    week_start: date | None = None,
    plan_type: CoachPlanType | None = None,
    status: CoachPlanStatus | None = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    return list_coach_plans(
        db,
        week_start=week_start,
        plan_type=plan_type,
        status=status,
        limit=limit,
    )


@router.get("/plans/{plan_id}", response_model=CoachPlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = get_coach_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
