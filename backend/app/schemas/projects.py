import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    description: str
    difficulty: str
    project_type: str


class ProjectDetail(ProjectSummary):
    rubric: dict


class ProjectSubmissionCreate(BaseModel):
    submission_url: str = Field(min_length=1, max_length=2048)


class ProjectSubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    submission_url: str | None
    status: str
    feedback: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
