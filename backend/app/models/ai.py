import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPkMixin

# Placeholder dimension — the real value is fixed once an embedding model is
# chosen in Phase 9 and must match that model exactly (e.g. 1536 for
# OpenAI-style embeddings, different for Voyage/Cohere).
EMBEDDING_DIM = 1536


class TutorMode(str, enum.Enum):
    """Fixed set of system-prompt templates selected by the backend — never
    free-form client text (Phase 1 §8)."""

    EXPLAIN = "explain"
    HINT = "hint"
    DEBUG = "debug"
    QUIZ_ME = "quiz_me"
    INTERVIEW_ME = "interview_me"
    REVIEW_CODE = "review_code"
    REVIEW_ANALYSIS = "review_analysis"
    EXPLAIN_GRAPH = "explain_graph"
    EXPLAIN_ERROR = "explain_error"
    GIVE_PROJECT = "give_project"
    CREATE_PRACTICE = "create_practice"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EmbeddingContentType(str, enum.Enum):
    LESSON = "lesson"
    GLOSSARY_TERM = "glossary_term"
    RESOURCE = "resource"
    TOOL = "tool"


class AISession(Base, UUIDPkMixin):
    __tablename__ = "ai_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mode: Mapped[TutorMode] = mapped_column(Enum(TutorMode, name="tutor_mode", native_enum=True), nullable=False)
    # lesson id, exercise id, dataset schema, etc. captured at session start —
    # the context-assembly snapshot described in Phase 1 §8.
    context: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    messages: Mapped[list["AIMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="AIMessage.created_at"
    )


class AIMessage(Base, UUIDPkMixin):
    __tablename__ = "ai_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, name="message_role", native_enum=True), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped["AISession"] = relationship(back_populates="messages")


class AIEmbedding(Base, UUIDPkMixin):
    """RAG index over curriculum content. Deliberately not a hard FK to each
    content table (that would require a polymorphic reference across four
    unrelated tables) — this table is a derived, fully rebuildable index, not
    a system of record, so content_id is an app-enforced reference only."""

    __tablename__ = "ai_embeddings"

    content_type: Mapped[EmbeddingContentType] = mapped_column(
        Enum(EmbeddingContentType, name="embedding_content_type", native_enum=True), nullable=False, index=True
    )
    content_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
