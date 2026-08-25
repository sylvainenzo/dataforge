from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.models.base import LearningLevel
from app.schemas.career import (
    CareerPathDetail,
    CareerPathProgress,
    CareerPathSkillRead,
    CareerPathSummary,
    InterviewQuestionRead,
    SkillProgress,
)
from app.services import career_service

router = APIRouter(tags=["career"])


@router.get("/interview-questions", response_model=list[InterviewQuestionRead])
async def list_interview_questions(
    category: str | None = None,
    difficulty: LearningLevel | None = None,
    career_path: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await career_service.list_interview_questions(
        db, category=category, difficulty=difficulty, career_path_slug=career_path
    )


@router.get("/interview-questions/categories", response_model=list[str])
async def list_interview_question_categories(db: AsyncSession = Depends(get_db)):
    return await career_service.list_interview_categories(db)


@router.get("/career-paths", response_model=list[CareerPathSummary])
async def list_career_paths(db: AsyncSession = Depends(get_db)):
    return await career_service.list_career_paths(db)


@router.get("/career-paths/{slug}", response_model=CareerPathDetail)
async def get_career_path(slug: str, db: AsyncSession = Depends(get_db)):
    result = await career_service.get_career_path_detail(db, slug)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career path not found")
    career_path, skills = result
    return CareerPathDetail(
        id=career_path.id,
        name=career_path.name,
        slug=career_path.slug,
        description=career_path.description,
        skills=[
            CareerPathSkillRead(skill_id=skill.id, skill_name=skill.name, skill_slug=skill.slug, weight=weight)
            for skill, weight in skills
        ],
    )


@router.get("/career-paths/{slug}/progress", response_model=CareerPathProgress)
async def get_career_path_progress(
    slug: str, current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    detail = await career_service.get_career_path_detail(db, slug)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career path not found")
    career_path, _ = detail

    result = await career_service.compute_career_progress(db, current_user.id, career_path.id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career path not found")
    name, skill_progress, overall = result

    return CareerPathProgress(
        career_path_id=career_path.id,
        career_path_name=name,
        overall_completion=overall,
        skills=[SkillProgress(**s) for s in skill_progress],
    )
