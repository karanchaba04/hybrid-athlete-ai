import hashlib
import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from hybrid_athlete_ai.config import settings
from hybrid_athlete_ai.models.db import CoachMessageORM, CoachPlanORM, CoachThreadORM
from hybrid_athlete_ai.models.enums import CoachPlanStatus, CoachPlanType
from hybrid_athlete_ai.schemas.coach import AccessoryRecommendation, CoachMessageRead, CoachPlanRead


def compute_context_hash(
    context_summary: dict[str, Any],
    *,
    available_slots: list[str] | None = None,
    notes: str | None = None,
) -> str:
    payload: dict[str, Any] = {"context": context_summary}
    if available_slots is not None:
        payload["available_slots"] = sorted(available_slots)
    if notes is not None:
        payload["notes"] = notes or ""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def find_active_plan(
    db: Session,
    *,
    week_start: date,
    plan_type: CoachPlanType,
    context_hash: str,
) -> CoachPlanORM | None:
    return (
        db.query(CoachPlanORM)
        .filter(
            CoachPlanORM.week_start == week_start,
            CoachPlanORM.plan_type == plan_type.value,
            CoachPlanORM.context_hash == context_hash,
            CoachPlanORM.status == CoachPlanStatus.ACTIVE.value,
        )
        .order_by(CoachPlanORM.created_at.desc())
        .first()
    )


def supersede_active_plans(
    db: Session,
    *,
    week_start: date,
    plan_type: CoachPlanType,
) -> None:
    active_plans = (
        db.query(CoachPlanORM)
        .filter(
            CoachPlanORM.week_start == week_start,
            CoachPlanORM.plan_type == plan_type.value,
            CoachPlanORM.status == CoachPlanStatus.ACTIVE.value,
        )
        .all()
    )
    for plan in active_plans:
        plan.status = CoachPlanStatus.SUPERSEDED.value


def save_coach_plan(
    db: Session,
    *,
    week_start: date,
    plan_type: CoachPlanType,
    context_hash: str,
    recommendation: AccessoryRecommendation,
    context_summary: dict[str, Any],
    request_payload: dict[str, Any] | None = None,
    supersede_existing: bool = True,
) -> CoachPlanORM:
    if supersede_existing:
        supersede_active_plans(db, week_start=week_start, plan_type=plan_type)

    plan = CoachPlanORM(
        week_start=week_start,
        plan_type=plan_type.value,
        context_hash=context_hash,
        recommendation_json=json.dumps(recommendation.model_dump(mode="json")),
        context_summary_json=json.dumps(context_summary, default=str),
        request_json=json.dumps(request_payload, default=str) if request_payload else None,
        model=settings.coach_model,
        status=CoachPlanStatus.ACTIVE.value,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def plan_to_read(plan: CoachPlanORM) -> CoachPlanRead:
    recommendation = AccessoryRecommendation.model_validate_json(plan.recommendation_json)
    context_summary = json.loads(plan.context_summary_json)
    request_payload = json.loads(plan.request_json) if plan.request_json else None
    return CoachPlanRead(
        id=plan.id,
        week_start=plan.week_start,
        plan_type=CoachPlanType(plan.plan_type),
        context_hash=plan.context_hash,
        recommendation=recommendation,
        context_summary=context_summary,
        request_payload=request_payload,
        model=plan.model,
        status=CoachPlanStatus(plan.status),
        created_at=plan.created_at,
    )


def list_coach_plans(
    db: Session,
    *,
    week_start: date | None = None,
    plan_type: CoachPlanType | None = None,
    status: CoachPlanStatus | None = None,
    limit: int = 20,
) -> list[CoachPlanRead]:
    query = db.query(CoachPlanORM)
    if week_start:
        query = query.filter(CoachPlanORM.week_start == week_start)
    if plan_type:
        query = query.filter(CoachPlanORM.plan_type == plan_type.value)
    if status:
        query = query.filter(CoachPlanORM.status == status.value)
    plans = query.order_by(CoachPlanORM.created_at.desc()).limit(limit).all()
    return [plan_to_read(plan) for plan in plans]


def get_coach_plan(db: Session, plan_id: int) -> CoachPlanRead | None:
    plan = db.query(CoachPlanORM).filter(CoachPlanORM.id == plan_id).first()
    if plan is None:
        return None
    return plan_to_read(plan)


def get_or_create_thread(
    db: Session,
    thread_id: str,
    *,
    week_start: date | None = None,
) -> CoachThreadORM:
    thread = db.query(CoachThreadORM).filter(CoachThreadORM.thread_id == thread_id).first()
    if thread is None:
        thread = CoachThreadORM(thread_id=thread_id, week_start=week_start)
        db.add(thread)
        db.commit()
        db.refresh(thread)
    return thread


def add_thread_message(
    db: Session,
    *,
    thread_id: str,
    role: str,
    content: str,
    week_start: date | None = None,
) -> CoachMessageORM:
    thread = get_or_create_thread(db, thread_id, week_start=week_start)
    message = CoachMessageORM(thread_id=thread.id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_thread_messages(db: Session, thread_id: str) -> list[CoachMessageRead]:
    thread = db.query(CoachThreadORM).filter(CoachThreadORM.thread_id == thread_id).first()
    if thread is None:
        return []
    return [
        CoachMessageRead(
            id=message.id,
            thread_id=thread_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        for message in thread.messages
    ]
