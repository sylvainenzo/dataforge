from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.schemas.projects import ProjectDetail, ProjectSubmissionCreate, ProjectSubmissionRead, ProjectSummary
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectSummary])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return await project_service.list_projects(db)


@router.get("/{slug}", response_model=ProjectDetail)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, slug)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/{slug}/submissions", response_model=ProjectSubmissionRead, status_code=status.HTTP_201_CREATED)
async def submit_project(
    slug: str,
    body: ProjectSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project = await project_service.get_project(db, slug)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return await project_service.create_submission(
        db, project_id=project.id, user_id=current_user.id, submission_url=body.submission_url
    )


@router.get("/{slug}/submissions", response_model=list[ProjectSubmissionRead])
async def list_my_submissions(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project = await project_service.get_project(db, slug)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return await project_service.list_user_submissions_for_project(db, project_id=project.id, user_id=current_user.id)
