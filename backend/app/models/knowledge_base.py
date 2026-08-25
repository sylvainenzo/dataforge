import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, LearningLevel, TimestampMixin, UUIDPkMixin


class Resource(Base, UUIDPkMixin, TimestampMixin):
    """url and last_verified_at are required — the admin content workflow is
    the only way rows are added; the AI tutor never writes to this table
    (Phase 1 §12/§28/§29)."""

    __tablename__ = "resources"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(160), nullable=False)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    level: Mapped[LearningLevel] = mapped_column(
        Enum(LearningLevel, name="learning_level", native_enum=True), nullable=False
    )
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    last_verified_at: Mapped[date] = mapped_column(Date, nullable=False)


class Tool(Base, UUIDPkMixin, TimestampMixin):
    """Column-for-column match of Phase 1 §57's tool schema."""

    __tablename__ = "tools"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    official_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    docs_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    mac_supported: Mapped[bool] = mapped_column(Boolean, nullable=False)
    apple_silicon_supported: Mapped[bool] = mapped_column(Boolean, nullable=False)
    intel_supported: Mapped[bool] = mapped_column(Boolean, nullable=False)
    install_method: Mapped[str] = mapped_column(String(255), nullable=False)
    homebrew_command: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verification_command: Mapped[str | None] = mapped_column(String(500), nullable=True)
    common_errors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    alternatives: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    last_verified_at: Mapped[date] = mapped_column(Date, nullable=False)

    install_guides: Mapped[list["InstallGuide"]] = relationship(back_populates="tool", cascade="all, delete-orphan")


class InstallGuide(Base, UUIDPkMixin, TimestampMixin):
    """content holds the full 16-part structure required by Phase 1 §13:
    what/why/when, install steps per architecture, verification, first
    project, common commands, errors, troubleshooting, updating,
    uninstalling, alternatives, docs link."""

    __tablename__ = "install_guides"

    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tools.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(Date, nullable=False)

    tool: Mapped["Tool"] = relationship(back_populates="install_guides")


class GlossaryTerm(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "glossary_terms"

    term: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    simple_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    technical_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)


class GlossaryTermRelation(Base):
    """Self-referential many-to-many for 'related concepts'."""

    __tablename__ = "glossary_term_relations"

    # No separate UniqueConstraint needed: the composite primary key below
    # already guarantees (term_id, related_term_id) uniqueness.
    term_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("glossary_terms.id", ondelete="CASCADE"), primary_key=True
    )
    related_term_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("glossary_terms.id", ondelete="CASCADE"), primary_key=True, index=True
    )
