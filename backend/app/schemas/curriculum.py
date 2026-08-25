import uuid

from pydantic import BaseModel, ConfigDict


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    category: str | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    order: int
    estimated_minutes: int | None = None


class LessonDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    order: int
    content: dict
    estimated_minutes: int | None = None
    skills: list[SkillRead] = []
    quiz_id: uuid.UUID | None = None


class ModuleWithLessons(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    order: int
    lessons: list[LessonSummary] = []


class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    level: str
    estimated_hours: int | None = None


class CourseDetail(CourseSummary):
    modules: list[ModuleWithLessons] = []
    completed_lesson_ids: list[uuid.UUID] = []


class LearningPathSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    description: str | None = None


class LearningPathDetail(LearningPathSummary):
    courses: list[CourseSummary] = []


class QuizQuestionPublic(BaseModel):
    """Correct answers are deliberately excluded — the client must never
    receive them before submitting an attempt."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_text: str
    question_type: str
    options: dict | None = None
    order: int
    points: int


class QuizDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    passing_score: int
    questions: list[QuizQuestionPublic] = []


class QuizAttemptSubmit(BaseModel):
    answers: dict[str, str]  # question_id (as str) -> submitted answer


class QuizAttemptResult(BaseModel):
    score: float
    passed: bool
    correct_count: int
    total_questions: int
