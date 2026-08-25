import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.base import DifficultyLevel, LearningLevel
from app.models.projects import ProjectSubmissionStatus, ProjectType


class AdminStats(BaseModel):
    user_count: int
    course_count: int
    lesson_count: int
    dataset_count: int
    project_count: int
    quiz_attempt_count: int
    code_execution_count: int


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime
    roles: list[str] = []


class SetUserRoleRequest(BaseModel):
    role: str
    grant: bool  # True to add the role, False to remove it


class AdminCourseCreate(BaseModel):
    title: str
    slug: str | None = None
    description: str | None = None
    level: LearningLevel
    estimated_hours: int | None = None
    published: bool = False


class AdminCourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    level: LearningLevel | None = None
    estimated_hours: int | None = None
    published: bool | None = None


class AdminModuleCreate(BaseModel):
    title: str
    slug: str | None = None
    order: int


class AdminModuleUpdate(BaseModel):
    title: str | None = None
    order: int | None = None


class AdminLessonCreate(BaseModel):
    title: str
    slug: str | None = None
    order: int
    content: dict = {}
    estimated_minutes: int | None = None
    published: bool = False


class AdminLessonUpdate(BaseModel):
    title: str | None = None
    order: int | None = None
    content: dict | None = None
    estimated_minutes: int | None = None
    published: bool | None = None


class AdminModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    slug: str
    order: int


class AdminLessonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    slug: str
    order: int
    content: dict
    estimated_minutes: int | None
    published: bool


class AdminQuizQuestionInput(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    options: dict | None = None
    correct_answer: dict
    explanation: str | None = None
    order: int
    points: int = 1


class AdminQuizCreate(BaseModel):
    title: str
    passing_score: int = 70
    questions: list[AdminQuizQuestionInput] = []


class AdminQuizUpdate(BaseModel):
    title: str | None = None
    passing_score: int | None = None
    questions: list[AdminQuizQuestionInput] | None = None


class AdminQuizQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_text: str
    question_type: str
    options: dict | None
    correct_answer: dict
    explanation: str | None
    order: int
    points: int


class AdminQuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    lesson_id: uuid.UUID | None
    title: str
    passing_score: int
    questions: list[AdminQuizQuestionRead] = []


class AdminCourseTreeLesson(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    order: int
    content: dict
    estimated_minutes: int | None
    published: bool
    quiz: AdminQuizRead | None = None


class AdminCourseTreeModule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    order: int
    lessons: list[AdminCourseTreeLesson] = []


class AdminCourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    description: str | None
    level: LearningLevel
    estimated_hours: int | None
    published: bool
    modules: list[AdminCourseTreeModule] = []


# ---- Resources & Glossary ----


class AdminResourceCreate(BaseModel):
    title: str
    provider: str
    level: LearningLevel
    is_free: bool
    description: str | None = None
    url: str
    last_verified_at: date


class AdminResourceUpdate(BaseModel):
    title: str | None = None
    provider: str | None = None
    level: LearningLevel | None = None
    is_free: bool | None = None
    description: str | None = None
    url: str | None = None
    last_verified_at: date | None = None


class AdminGlossaryTermCreate(BaseModel):
    term: str
    slug: str | None = None
    simple_explanation: str
    technical_explanation: str | None = None
    example: str | None = None


class AdminGlossaryTermUpdate(BaseModel):
    term: str | None = None
    simple_explanation: str | None = None
    technical_explanation: str | None = None
    example: str | None = None


# ---- Tools ----


class AdminToolCreate(BaseModel):
    name: str
    slug: str | None = None
    description: str
    category: str
    official_url: str
    docs_url: str | None = None
    mac_supported: bool
    apple_silicon_supported: bool
    intel_supported: bool
    install_method: str
    homebrew_command: str | None = None
    verification_command: str | None = None
    common_errors: dict | None = None
    alternatives: list[str] | None = None
    last_verified_at: date


class AdminToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    official_url: str | None = None
    docs_url: str | None = None
    mac_supported: bool | None = None
    apple_silicon_supported: bool | None = None
    intel_supported: bool | None = None
    install_method: str | None = None
    homebrew_command: str | None = None
    verification_command: str | None = None
    common_errors: dict | None = None
    alternatives: list[str] | None = None
    last_verified_at: date | None = None


class AdminToolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str
    category: str
    official_url: str
    docs_url: str | None
    mac_supported: bool
    apple_silicon_supported: bool
    intel_supported: bool
    install_method: str
    homebrew_command: str | None
    verification_command: str | None
    common_errors: dict | None
    alternatives: list[str] | None
    last_verified_at: date


# ---- Career paths ----


class AdminCareerPathCreate(BaseModel):
    name: str
    slug: str | None = None
    description: str | None = None
    skill_weights: dict[str, float] = {}  # skill slug -> weight


class AdminCareerPathUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    skill_weights: dict[str, float] | None = None


class AdminCareerPathRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    skill_weights: dict[str, float] = {}


# ---- Interview questions ----


class AdminInterviewQuestionCreate(BaseModel):
    question: str
    category: str
    difficulty: LearningLevel
    sample_answer: str
    career_path_id: uuid.UUID | None = None


class AdminInterviewQuestionUpdate(BaseModel):
    question: str | None = None
    category: str | None = None
    difficulty: LearningLevel | None = None
    sample_answer: str | None = None
    career_path_id: uuid.UUID | None = None


class AdminInterviewQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question: str
    category: str
    difficulty: LearningLevel
    sample_answer: str
    career_path_id: uuid.UUID | None


# ---- Projects ----


class AdminProjectCreate(BaseModel):
    title: str
    slug: str | None = None
    description: str
    difficulty: DifficultyLevel
    project_type: ProjectType
    dataset_id: uuid.UUID | None = None
    rubric: dict = {}


class AdminProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    project_type: ProjectType | None = None
    dataset_id: uuid.UUID | None = None
    rubric: dict | None = None


class AdminProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    slug: str
    description: str
    difficulty: str
    project_type: str
    dataset_id: uuid.UUID | None
    rubric: dict


# ---- Project submissions (review queue) ----


class AdminProjectSubmissionReview(BaseModel):
    status: ProjectSubmissionStatus
    feedback: str | None = None


class AdminProjectSubmissionRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_title: str
    user_id: uuid.UUID
    user_email: str
    submission_url: str | None
    status: str
    feedback: str | None
    submitted_at: datetime
    reviewed_at: datetime | None


# ---- Datasets ----


class AdminDatasetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    domain: str | None = None
    difficulty: DifficultyLevel | None = None


class AdminDatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    source: str
    source_url: str
    license: str
    domain: str | None
    difficulty: str
    format: str
