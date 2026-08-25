import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Flashcard(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "flashcards"

    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    # Nullable: system-generated flashcards (e.g. auto-derived from glossary
    # terms) have no authoring user.
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )


class SpacedRepetitionLog(Base, UUIDPkMixin):
    """SM-2 scheduling state per (user, flashcard) — Phase 1 §38."""

    __tablename__ = "spaced_repetition_logs"
    __table_args__ = (Index("uq_spaced_rep_user_flashcard", "user_id", "flashcard_id", unique=True),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ease_factor: Mapped[float] = mapped_column(Numeric(4, 2), default=2.5, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_grade: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)


class UserProgress(Base, UUIDPkMixin):
    """The single source every dashboard widget reads from (Phase 1 §15).

    Modeled as one physical table with three nullable, individually
    FK-constrained scope columns rather than a polymorphic (scope_type,
    scope_id) pair, so referential integrity is enforced by Postgres itself
    rather than application code. The CHECK constraint keeps each row scoped
    to exactly one of lesson / course / skill; the three partial unique
    indexes enforce one progress row per (user, target) within each scope.
    """

    __tablename__ = "user_progress"
    __table_args__ = (
        CheckConstraint(
            "(num_nonnulls(lesson_id, course_id, skill_id) = 1)",
            name="ck_user_progress_single_scope",
        ),
        Index(
            "uq_user_progress_lesson",
            "user_id",
            "lesson_id",
            unique=True,
            postgresql_where=text("lesson_id IS NOT NULL"),
        ),
        Index(
            "uq_user_progress_course",
            "user_id",
            "course_id",
            unique=True,
            postgresql_where=text("course_id IS NOT NULL"),
        ),
        Index(
            "uq_user_progress_skill",
            "user_id",
            "skill_id",
            unique=True,
            postgresql_where=text("skill_id IS NOT NULL"),
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True
    )
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=True
    )
    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=True
    )
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus, name="progress_status", native_enum=True), nullable=False
    )
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
