import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import QuizAttempt
from app.models.datasets import DatasetVersion
from app.models.gamification import Achievement, Badge
from app.models.learning_science import ProgressStatus, UserProgress
from app.models.platform import AuditLog

XP_PER_COMPLETED_LESSON = 10
XP_PER_PASSED_QUIZ = 15

# Criteria evaluated against real activity tables — no fabricated/mutable
# counters (Phase 1 §15/§40). Each achievement is checked and (idempotently)
# awarded whenever a caller asks "what has this user earned so far".
ACHIEVEMENT_DEFINITIONS = [
    {
        "key": "first_lesson_completed",
        "name": "First Lesson Complete",
        "description": "Completed your first lesson.",
        "xp_reward": 20,
        "icon": "book-open",
    },
    {
        "key": "first_quiz_passed",
        "name": "Quiz Whiz",
        "description": "Passed your first quiz.",
        "xp_reward": 20,
        "icon": "check-circle",
    },
    {
        "key": "first_python_run",
        "name": "Hello, Python",
        "description": "Ran your first Python code in the sandbox.",
        "xp_reward": 15,
        "icon": "code",
    },
    {
        "key": "first_sql_query",
        "name": "First Query",
        "description": "Ran your first SQL query.",
        "xp_reward": 15,
        "icon": "database",
    },
    {
        "key": "first_dataset_uploaded",
        "name": "Data Wrangler",
        "description": "Uploaded and profiled your first dataset.",
        "xp_reward": 25,
        "icon": "upload",
    },
]


async def _count_completed_lessons(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.is_not(None),
            UserProgress.status == ProgressStatus.COMPLETED,
        )
    )
    return result.scalar_one()


async def _count_passed_quizzes(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).where(QuizAttempt.user_id == user_id, QuizAttempt.passed.is_(True))
    )
    return result.scalar_one()


async def _count_audit_actions(db: AsyncSession, user_id: uuid.UUID, action: str) -> int:
    result = await db.execute(select(func.count()).where(AuditLog.user_id == user_id, AuditLog.action == action))
    return result.scalar_one()


async def _count_dataset_uploads(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(select(func.count()).where(DatasetVersion.uploaded_by == user_id))
    return result.scalar_one()


async def sync_achievements(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    """Checks every achievement's real-activity criteria and awards any
    newly-earned ones. Returns the keys of achievements newly awarded this
    call (empty most of the time — it's idempotent)."""

    counts = {
        "first_lesson_completed": await _count_completed_lessons(db, user_id),
        "first_quiz_passed": await _count_passed_quizzes(db, user_id),
        "first_python_run": await _count_audit_actions(db, user_id, "code_execution"),
        "first_sql_query": await _count_audit_actions(db, user_id, "sql_query"),
        "first_dataset_uploaded": await _count_dataset_uploads(db, user_id),
    }

    existing_badges = await db.execute(
        select(Achievement.key).join(Badge, Badge.achievement_id == Achievement.id).where(Badge.user_id == user_id)
    )
    already_earned = set(existing_badges.scalars().all())

    newly_awarded = []
    for definition in ACHIEVEMENT_DEFINITIONS:
        key = definition["key"]
        if key in already_earned or counts.get(key, 0) < 1:
            continue

        result = await db.execute(select(Achievement).where(Achievement.key == key))
        achievement = result.scalar_one_or_none()
        if achievement is None:
            continue  # not seeded yet — sync_achievements is safe to call before seeding

        db.add(Badge(user_id=user_id, achievement_id=achievement.id))
        newly_awarded.append(key)

    if newly_awarded:
        await db.commit()
    return newly_awarded


async def compute_xp(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Derived, not stored — recomputed from real rows every time, so it
    can never drift from what actually happened (Phase 1 §15)."""

    lessons = await _count_completed_lessons(db, user_id)
    quizzes = await _count_passed_quizzes(db, user_id)

    badge_result = await db.execute(
        select(func.coalesce(func.sum(Achievement.xp_reward), 0))
        .join(Badge, Badge.achievement_id == Achievement.id)
        .where(Badge.user_id == user_id)
    )
    achievement_xp = badge_result.scalar_one()

    return lessons * XP_PER_COMPLETED_LESSON + quizzes * XP_PER_PASSED_QUIZ + int(achievement_xp)


async def compute_streak(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Consecutive days (ending today or yesterday) with at least one real
    activity event — lesson progress, a quiz attempt, or a logged
    execution/SQL run."""

    since = datetime.now(UTC) - timedelta(days=60)

    progress_dates = await db.execute(
        select(func.date(UserProgress.updated_at)).where(
            UserProgress.user_id == user_id, UserProgress.updated_at >= since
        )
    )
    quiz_dates = await db.execute(
        select(func.date(QuizAttempt.completed_at)).where(
            QuizAttempt.user_id == user_id, QuizAttempt.completed_at >= since
        )
    )
    audit_dates = await db.execute(
        select(func.date(AuditLog.created_at)).where(AuditLog.user_id == user_id, AuditLog.created_at >= since)
    )

    active_days = set(progress_dates.scalars().all())
    active_days |= {row for row in quiz_dates.scalars().all() if row is not None}
    active_days |= set(audit_dates.scalars().all())

    if not active_days:
        return 0

    today = datetime.now(UTC).date()
    streak = 0
    cursor = today if today in active_days else today - timedelta(days=1)
    if cursor not in active_days:
        return 0

    while cursor in active_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


async def get_earned_badges(db: AsyncSession, user_id: uuid.UUID) -> list[Achievement]:
    result = await db.execute(
        select(Achievement).join(Badge, Badge.achievement_id == Achievement.id).where(Badge.user_id == user_id)
    )
    return list(result.scalars().all())
