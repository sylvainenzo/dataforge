import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.base import LearningLevel


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    provider: str
    level: LearningLevel
    is_free: bool
    description: str | None
    url: str
    last_verified_at: date


class GlossaryTermRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    term: str
    slug: str
    simple_explanation: str
    technical_explanation: str | None
    example: str | None
