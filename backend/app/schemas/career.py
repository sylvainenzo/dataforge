import uuid

from pydantic import BaseModel, ConfigDict

from app.models.base import LearningLevel


class CareerPathSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str | None


class CareerPathSkillRead(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    skill_slug: str
    weight: float


class CareerPathDetail(CareerPathSummary):
    skills: list[CareerPathSkillRead]


class SkillProgress(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    skill_slug: str
    weight: float
    lessons_completed: int
    lessons_total: int
    completion: float


class CareerPathProgress(BaseModel):
    career_path_id: uuid.UUID
    career_path_name: str
    overall_completion: float
    skills: list[SkillProgress]


class InterviewQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question: str
    category: str
    difficulty: LearningLevel
    sample_answer: str
    career_path_id: uuid.UUID | None
