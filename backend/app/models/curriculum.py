import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, LearningLevel, TimestampMixin, UUIDPkMixin


class Skill(Base, UUIDPkMixin, TimestampMixin):
    """The taxonomy shared across curriculum, gamification ('what am I weak
    at'), and career-path progress — see Phase 1 §10/§15/§16."""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)


class Topic(Base, UUIDPkMixin, TimestampMixin):
    """Cross-cutting tag (e.g. 'Python', 'SQL', 'Statistics') used for search
    and glossary organization — distinct from the hierarchical course tree."""

    __tablename__ = "topics"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class LearningPath(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "learning_paths"

    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_path_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("career_paths.id", ondelete="SET NULL"), nullable=True, index=True
    )
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    courses: Mapped[list["LearningPathCourse"]] = relationship(
        back_populates="learning_path", cascade="all, delete-orphan", order_by="LearningPathCourse.order"
    )


class Course(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[LearningLevel] = mapped_column(
        Enum(LearningLevel, name="learning_level", native_enum=True), nullable=False
    )
    estimated_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    modules: Mapped[list["Module"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="Module.order"
    )


class LearningPathCourse(Base):
    """Ordered many-to-many between learning_paths and courses."""

    __tablename__ = "learning_path_courses"

    learning_path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), primary_key=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    learning_path: Mapped["LearningPath"] = relationship(back_populates="courses")
    course: Mapped["Course"] = relationship()


class Module(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="uq_module_course_slug"),
        UniqueConstraint("course_id", "order", name="uq_module_course_order"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order"
    )


class Lesson(Base, UUIDPkMixin, TimestampMixin):
    """content is structured JSON content blocks (objectives, explanation,
    example, code, exercise, quiz, challenge, summary, ...) per Phase 1 §10 —
    each block is rendered by a typed frontend component, not one markdown
    blob."""

    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("module_id", "slug", name="uq_lesson_module_slug"),)

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    module: Mapped["Module"] = relationship(back_populates="lessons")
    # One-to-one in practice (every seeded lesson has at most one quiz) even
    # though Quiz.lesson_id is nullable to also allow standalone quizzes.
    quiz: Mapped["Quiz | None"] = relationship(viewonly=True, uselist=False)


class LessonSkill(Base):
    __tablename__ = "lesson_skills"

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True
    )


class LessonTopic(Base):
    __tablename__ = "lesson_topics"

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True, index=True
    )
