from pydantic import BaseModel, Field


class CoachChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(default="default", max_length=128)


class CoachChatResponse(BaseModel):
    response: str
    thread_id: str


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


class AccessoryPlanResponse(BaseModel):
    recommendation: AccessoryRecommendation
    context_summary: dict
