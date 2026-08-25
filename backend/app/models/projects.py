import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, DifficultyLevel, TimestampMixin, UUIDPkMixin


class ProjectType(str, enum.Enum):
    """Matches Phase 1 §32 Project Types."""

    EDA = "eda"
    DASHBOARD = "dashboard"
    SQL_ANALYSIS = "sql_analysis"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    PREDICTIVE_MODELING = "predictive_modeling"
    FORECASTING = "forecasting"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION_SYSTEM = "recommendation_system"
    DATA_ENGINEERING = "data_engineering"
    MLOPS = "mlops"
    GENERATIVE_AI = "generative_ai"
    REAL_TIME_ANALYTICS = "real_time_analytics"


class ProjectSubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    PASSED = "passed"


class Project(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", native_enum=True), nullable=False
    )
    project_type: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType, name="project_type", native_enum=True), nullable=False
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Objectives, questions, skills, tools, steps, deliverables, evaluation
    # rubric — the Project Factory output shape from Phase 1 §31.
    rubric: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class ProjectSubmission(Base, UUIDPkMixin):
    __tablename__ = "project_submissions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    submission_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[ProjectSubmissionStatus] = mapped_column(
        Enum(ProjectSubmissionStatus, name="project_submission_status", native_enum=True),
        nullable=False,
        default=ProjectSubmissionStatus.SUBMITTED,
    )
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
