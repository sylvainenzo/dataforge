import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import LearningLevel
from app.models.career import CareerPath, CareerPathSkill, InterviewQuestion
from app.models.curriculum import Lesson, LessonSkill, Skill
from app.models.learning_science import ProgressStatus, UserProgress


async def list_career_paths(db: AsyncSession) -> list[CareerPath]:
    result = await db.execute(select(CareerPath).order_by(CareerPath.name))
    return list(result.scalars().all())


async def get_career_path_detail(db: AsyncSession, slug: str) -> tuple[CareerPath, list[tuple[Skill, float]]] | None:
    result = await db.execute(select(CareerPath).where(CareerPath.slug == slug))
    career_path = result.scalar_one_or_none()
    if career_path is None:
        return None

    skills_result = await db.execute(
        select(Skill, CareerPathSkill.weight)
        .join(CareerPathSkill, CareerPathSkill.skill_id == Skill.id)
        .where(CareerPathSkill.career_path_id == career_path.id)
        .order_by(CareerPathSkill.weight.desc())
    )
    skills = [(skill, float(weight)) for skill, weight in skills_result.all()]
    return career_path, skills


async def compute_career_progress(
    db: AsyncSession, user_id: uuid.UUID, career_path_id: uuid.UUID
) -> tuple[str, list[dict], float] | None:
    """Real-activity-derived, like gamification: completion per skill comes
    from actually-completed lessons tagged with that skill, never a stored
    counter that could drift from reality."""

    cp_result = await db.execute(select(CareerPath).where(CareerPath.id == career_path_id))
    career_path = cp_result.scalar_one_or_none()
    if career_path is None:
        return None

    skills_result = await db.execute(
        select(Skill, CareerPathSkill.weight)
        .join(CareerPathSkill, CareerPathSkill.skill_id == Skill.id)
        .where(CareerPathSkill.career_path_id == career_path_id)
    )
    skills = skills_result.all()

    skill_progress = []
    for skill, weight in skills:
        total_result = await db.execute(
            select(func.count()).select_from(LessonSkill).join(Lesson).where(LessonSkill.skill_id == skill.id)
        )
        total = total_result.scalar_one()

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

        completion = (completed / total) if total > 0 else 0.0
        skill_progress.append(
            {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "skill_slug": skill.slug,
                "weight": float(weight),
                "lessons_completed": completed,
                "lessons_total": total,
                "completion": round(completion, 4),
            }
        )

    total_weight = sum(s["weight"] for s in skill_progress)
    overall = (
        sum(s["weight"] * s["completion"] for s in skill_progress) / total_weight if total_weight > 0 else 0.0
    )

    return career_path.name, skill_progress, round(overall, 4)


async def list_interview_questions(
    db: AsyncSession,
    *,
    category: str | None = None,
    difficulty: LearningLevel | None = None,
    career_path_slug: str | None = None,
) -> list[InterviewQuestion]:
    query = select(InterviewQuestion).order_by(InterviewQuestion.category, InterviewQuestion.difficulty)
    if category is not None:
        query = query.where(InterviewQuestion.category == category)
    if difficulty is not None:
        query = query.where(InterviewQuestion.difficulty == difficulty)
    if career_path_slug is not None:
        query = query.join(CareerPath, CareerPath.id == InterviewQuestion.career_path_id).where(
            CareerPath.slug == career_path_slug
        )
    result = await db.execute(query)
    return list(result.scalars().all())


async def list_interview_categories(db: AsyncSession) -> list[str]:
    result = await db.execute(select(InterviewQuestion.category).distinct().order_by(InterviewQuestion.category))
    return list(result.scalars().all())
