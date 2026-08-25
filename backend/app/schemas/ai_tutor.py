import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.ai import TutorMode


class CreateSessionRequest(BaseModel):
    mode: TutorMode
    lesson_title: str | None = None
    code: str | None = None
    error_message: str | None = None
    skill_level: str | None = None


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    mode: TutorMode
    started_at: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
