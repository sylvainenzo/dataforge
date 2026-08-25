import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class Achievement(Base, UUIDPkMixin, TimestampMixin):
    """Definitions catalog — e.g. 'first_sql_query', 'data_cleaning_specialist'
    (Phase 1 §40). criteria is a machine-readable unlock condition evaluated
    by the gamification service against the activity log, not by this table."""

    __tablename__ = "achievements"

    key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(120), nullable=True)
    criteria: Mapped[dict] = mapped_column(JSONB, nullable=False)


class Badge(Base, UUIDPkMixin):
    """An earned achievement instance — kept separate from Achievement so the
    catalog can evolve without touching historical earn records."""

    __tablename__ = "badges"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_badge_user_achievement"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Certificate(Base, UUIDPkMixin):
    """'Certificate of Platform Completion' only — never claims university
    accreditation (Phase 1 §41). Scoped to exactly one of learning_path or
    course, mirroring the UserProgress pattern in learning_science.py."""

    __tablename__ = "certificates"
    __table_args__ = (
        CheckConstraint(
            "(num_nonnulls(learning_path_id, course_id) = 1)",
            name="ck_certificate_single_scope",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    learning_path_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=True
    )
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    certificate_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    pdf_storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
