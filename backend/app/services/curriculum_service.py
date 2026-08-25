import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import Quiz, QuizAttempt
from app.models.curriculum import Course, LearningPath, LearningPathCourse, Lesson, LessonSkill, Module, Skill
from app.models.learning_science import ProgressStatus, UserProgress


async def list_learning_paths(db: AsyncSession) -> list[LearningPath]:
    result = await db.execute(select(LearningPath).where(LearningPath.published == True))  # noqa: E712
    return list(result.scalars().all())


async def get_learning_path(db: AsyncSession, slug: str) -> LearningPath | None:
    result = await db.execute(
        select(LearningPath)
        .options(selectinload(LearningPath.courses).selectinload(LearningPathCourse.course))
        .where(LearningPath.slug == slug)
    )
    return result.scalar_one_or_none()


async def list_courses(db: AsyncSession) -> list[Course]:
    result = await db.execute(select(Course).where(Course.published == True))  # noqa: E712
    return list(result.scalars().all())


async def get_course_detail(db: AsyncSession, slug: str) -> Course | None:
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.modules).selectinload(Module.lessons))
        .where(Course.slug == slug, Course.published == True)  # noqa: E712
    )
    return result.scalar_one_or_none()


async def get_lesson_detail(db: AsyncSession, slug: str) -> Lesson | None:
    result = await db.execute(select(Lesson).where(Lesson.slug == slug, Lesson.published == True))  # noqa: E712
    lesson = result.scalar_one_or_none()
    return lesson


async def get_completed_lesson_ids(
    db: AsyncSession, *, user_id: uuid.UUID, lesson_ids: list[uuid.UUID]
) -> list[uuid.UUID]:
    if not lesson_ids:
        return []
    result = await db.execute(
        select(UserProgress.lesson_id).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.status == ProgressStatus.COMPLETED,
        )
    )
    return list(result.scalars().all())


async def get_lesson_skills(db: AsyncSession, lesson_id: uuid.UUID) -> list[Skill]:
    result = await db.execute(
        select(Skill).join(LessonSkill, LessonSkill.skill_id == Skill.id).where(LessonSkill.lesson_id == lesson_id)
    )
    return list(result.scalars().all())


async def mark_lesson_progress(
    db: AsyncSession, *, user_id: uuid.UUID, lesson_id: uuid.UUID, status: ProgressStatus
) -> None:
    existing = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id, UserProgress.lesson_id == lesson_id)
    )
    row = existing.scalar_one_or_none()
    now = datetime.now(UTC)

    # Re-visiting a lesson (GET /lessons/{slug} on every view) must never
    # downgrade an already-completed lesson back to in-progress — this was
    # a real bug: opening a finished lesson again silently lost the
    # completion. Only a state that isn't a downgrade is ever applied.
    if row is not None and row.status == ProgressStatus.COMPLETED and status != ProgressStatus.COMPLETED:
        return

    if row is None:
        row = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status=status,
            progress_percent=100 if status == ProgressStatus.COMPLETED else 50,
            completed_at=now if status == ProgressStatus.COMPLETED else None,
        )
        db.add(row)
    else:
        row.status = status
        row.progress_percent = 100 if status == ProgressStatus.COMPLETED else 50
        if status == ProgressStatus.COMPLETED:
            row.completed_at = now
    await db.commit()


async def get_quiz_detail(db: AsyncSession, quiz_id: uuid.UUID) -> Quiz | None:
    result = await db.execute(
        select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
    )
    return result.scalar_one_or_none()


async def get_quiz_for_lesson(db: AsyncSession, lesson_id: uuid.UUID) -> Quiz | None:
    result = await db.execute(select(Quiz).where(Quiz.lesson_id == lesson_id))
    return result.scalar_one_or_none()


async def submit_quiz_attempt(
    db: AsyncSession, *, user_id: uuid.UUID, quiz: Quiz, answers: dict[str, str]
) -> tuple[float, bool, int]:
    """Grades server-side against QuizQuestion.correct_answer — the client
    only ever sees QuizQuestionPublic, which excludes answers."""

    total_points = sum(q.points for q in quiz.questions)
    earned_points = 0
    correct_count = 0

    for question in quiz.questions:
        submitted = answers.get(str(question.id))
        correct = question.correct_answer.get("value") if isinstance(question.correct_answer, dict) else None
        if submitted is not None and correct is not None and submitted.strip().lower() == str(correct).strip().lower():
            earned_points += question.points
            correct_count += 1

    score = round((earned_points / total_points) * 100, 2) if total_points else 0.0
    passed = score >= quiz.passing_score

    now = datetime.now(UTC)
    db.add(
        QuizAttempt(
            quiz_id=quiz.id,
            user_id=user_id,
            score=score,
            passed=passed,
            answers=answers,
            started_at=now,
            completed_at=now,
        )
    )
    await db.commit()
    return score, passed, correct_count
