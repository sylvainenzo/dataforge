import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum import Course
from app.models.gamification import Certificate
from app.models.identity import Profile
from app.models.projects import Project, ProjectSubmission, ProjectSubmissionStatus


async def get_portfolio_settings(db: AsyncSession, user_id: uuid.UUID) -> Profile | None:
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def update_portfolio_settings(
    db: AsyncSession, user_id: uuid.UUID, *, bio: str | None = None, portfolio_public: bool | None = None
) -> Profile:
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one()
    if bio is not None:
        profile.bio = bio
    if portfolio_public is not None:
        profile.portfolio_public = portfolio_public
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_public_portfolio(db: AsyncSession, user_id: uuid.UUID) -> dict | None:
    profile_result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    profile = profile_result.scalar_one_or_none()
    if profile is None or not profile.portfolio_public:
        return None

    submissions_result = await db.execute(
        select(Project.title, Project.slug, ProjectSubmission.submission_url, ProjectSubmission.reviewed_at)
        .join(Project, Project.id == ProjectSubmission.project_id)
        .where(
            ProjectSubmission.user_id == user_id,
            ProjectSubmission.status == ProjectSubmissionStatus.PASSED,
        )
        .order_by(ProjectSubmission.reviewed_at.desc())
    )
    projects = [
        {"project_title": title, "project_slug": slug, "submission_url": url, "reviewed_at": reviewed_at}
        for title, slug, url, reviewed_at in submissions_result.all()
    ]

    certificates_result = await db.execute(
        select(Course.title, Certificate.certificate_number, Certificate.issued_at)
        .join(Course, Course.id == Certificate.course_id)
        .where(Certificate.user_id == user_id)
        .order_by(Certificate.issued_at.desc())
    )
    certificates = [
        {"course_title": title, "certificate_number": number, "issued_at": issued_at}
        for title, number, issued_at in certificates_result.all()
    ]

    return {
        "user_id": user_id,
        "display_name": profile.display_name,
        "bio": profile.bio,
        "projects": projects,
        "certificates": certificates,
    }
