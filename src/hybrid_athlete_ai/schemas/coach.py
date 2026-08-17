from pydantic import BaseModel, Field


class CoachChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(default="default", max_length=128)


class CoachChatResponse(BaseModel):
    response: str
    thread_id: str
