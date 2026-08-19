from datetime import date, datetime

from pydantic import BaseModel, Field

from hybrid_athlete_ai.models.enums import CoachPlanStatus, CoachPlanType


class CoachChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(default="default", max_length=128)


class CoachChatResponse(BaseModel):
    response: str
    thread_id: str


class CoachMessageRead(BaseModel):
    id: int
    thread_id: str
    role: str
    content: str
    created_at: datetime | None = None


class AccessoryExercise(BaseModel):
    name: str
    prescription: str = Field(description="e.g. 4×5 @ 70 kg or 3×10 @ RPE 7")
    notes: str | None = None


class AccessorySlotPlan(BaseModel):
    slot: str = Field(description="Matches one of the requested time slots")
    exercises: list[AccessoryExercise]


class AccessoryRecommendation(BaseModel):
    slots: list[AccessorySlotPlan]
    rationale: str
    warnings: list[str] = Field(default_factory=list)


class AccessoryPlanRequest(BaseModel):
    available_slots: list[str] = Field(
        min_length=1,
        max_length=7,
        description="e.g. ['Tue 30 min', 'Thu 45 min', 'Sat 30 min']",
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional context: nagging shoulder, travel week, etc.",
    )
    force_regenerate: bool = Field(
        default=False,
        description="Skip cache and generate a new plan (supersedes current active plan for the week).",
    )


class AccessoryPlanResponse(BaseModel):
    recommendation: AccessoryRecommendation
    context_summary: dict
    plan_id: int | None = None
    from_cache: bool = False
    context_hash: str | None = None


class CoachPlanRead(BaseModel):
    id: int
    week_start: date
    plan_type: CoachPlanType
    context_hash: str
    recommendation: AccessoryRecommendation
    context_summary: dict
    request_payload: dict | None = None
    model: str
    status: CoachPlanStatus
    created_at: datetime | None = None
