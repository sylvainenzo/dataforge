import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project, ProjectSubmission


async def list_projects(db: AsyncSession) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.title))
    return list(result.scalars().all())


async def get_project(db: AsyncSession, slug: str) -> Project | None:
    result = await db.execute(select(Project).where(Project.slug == slug))
    return result.scalar_one_or_none()


async def create_submission(db: AsyncSession, *, project_id: uuid.UUID, user_id: uuid.UUID, submission_url: str) -> ProjectSubmission:
    submission = ProjectSubmission(project_id=project_id, user_id=user_id, submission_url=submission_url)
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def list_user_submissions_for_project(
    db: AsyncSession, *, project_id: uuid.UUID, user_id: uuid.UUID
) -> list[ProjectSubmission]:
    result = await db.execute(
        select(ProjectSubmission)
        .where(ProjectSubmission.project_id == project_id, ProjectSubmission.user_id == user_id)
        .order_by(ProjectSubmission.submitted_at.desc())
    )
    return list(result.scalars().all())
