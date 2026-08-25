import uuid

from pydantic import BaseModel


class RecommendedLesson(BaseModel):
    slug: str
    title: str


class SkillRecommendation(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    skill_slug: str
    lessons_completed: int
    lessons_total: int
    completion: float
    next_lesson: RecommendedLesson | None
