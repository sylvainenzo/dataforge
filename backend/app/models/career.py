import uuid

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, LearningLevel, TimestampMixin, UUIDPkMixin


class CareerPath(Base, UUIDPkMixin, TimestampMixin):
    """Data Analyst, Data Scientist, Data Engineer, ML Engineer, Analytics
    Engineer, BI Analyst — Phase 1 §16/§45."""

    __tablename__ = "career_paths"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class CareerPathSkill(Base):
    """Weighted skill requirement — drives the career-progress dashboard
    widget (Phase 1 §31)."""

    __tablename__ = "career_path_skills"

    career_path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("career_paths.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    weight: Mapped[float] = mapped_column(Numeric(4, 2), default=1.0, nullable=False)


class InterviewQuestion(Base, UUIDPkMixin, TimestampMixin):
    """Browsable interview-prep bank, optionally scoped to a career path."""

    __tablename__ = "interview_questions"

    question: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    difficulty: Mapped[LearningLevel] = mapped_column(
        Enum(LearningLevel, name="learning_level", native_enum=True), nullable=False
    )
    sample_answer: Mapped[str] = mapped_column(Text, nullable=False)
    career_path_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("career_paths.id", ondelete="SET NULL"), nullable=True, index=True
    )
