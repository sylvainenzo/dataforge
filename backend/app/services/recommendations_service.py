import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum import Lesson, LessonSkill, Module, Skill
from app.models.learning_science import ProgressStatus, UserProgress


async def get_skill_recommendations(db: AsyncSession, user_id: uuid.UUID, limit: int = 3) -> list[dict]:
    """Real-activity-derived, same pattern as career-path progress: no
    stored 'weak skill' flag anywhere — completion is computed live from
    UserProgress every time this is called, so it can never drift from
    what the learner has actually done.

    Recommends the skills the learner has genuinely started but not
    finished first (most actionable — "you're partway through this"), and
    only falls back to entirely untouched skills if there aren't enough
    in-progress ones to fill out the list.
    """

    skills_result = await db.execute(select(Skill).order_by(Skill.name))
    skills = list(skills_result.scalars().all())

    rows: list[dict] = []
    for skill in skills:
        total_result = await db.execute(
            select(func.count()).select_from(LessonSkill).join(Lesson).where(LessonSkill.skill_id == skill.id)
        )
        total = total_result.scalar_one()
        if total == 0:
            continue

        completed_result = await db.execute(
            select(func.count())
            .select_from(LessonSkill)
            .join(Lesson, Lesson.id == LessonSkill.lesson_id)
            .join(
                UserProgress,
                (UserProgress.lesson_id == Lesson.id)
                & (UserProgress.user_id == user_id)
                & (UserProgress.status == ProgressStatus.COMPLETED),
            )
            .where(LessonSkill.skill_id == skill.id)
        )
        completed = completed_result.scalar_one()

        if completed >= total:
            continue  # already mastered — nothing to recommend here

        next_lesson_result = await db.execute(
            select(Lesson.slug, Lesson.title)
            .select_from(LessonSkill)
            .join(Lesson, Lesson.id == LessonSkill.lesson_id)
            .join(Module, Module.id == Lesson.module_id)
            .outerjoin(
                UserProgress,
                (UserProgress.lesson_id == Lesson.id)
                & (UserProgress.user_id == user_id)
                & (UserProgress.status == ProgressStatus.COMPLETED),
            )
            .where(LessonSkill.skill_id == skill.id, UserProgress.id.is_(None))
            .order_by(Module.order, Lesson.order)
            .limit(1)
        )
        next_lesson_row = next_lesson_result.first()

        rows.append(
            {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "skill_slug": skill.slug,
                "lessons_completed": completed,
                "lessons_total": total,
                "completion": round(completed / total, 4),
                "next_lesson": {"slug": next_lesson_row.slug, "title": next_lesson_row.title} if next_lesson_row else None,
            }
        )

    in_progress = [r for r in rows if r["lessons_completed"] > 0]
    not_started = [r for r in rows if r["lessons_completed"] == 0]
    in_progress.sort(key=lambda r: r["completion"])

    return (in_progress + not_started)[:limit]
