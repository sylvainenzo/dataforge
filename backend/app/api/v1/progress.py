import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.schemas.gamification import (
    FlashcardRead,
    FlashcardReviewRequest,
    FlashcardReviewResult,
    ProgressSummary,
)
from app.schemas.recommendations import SkillRecommendation
from app.services import flashcard_service, gamification_service, recommendations_service

router = APIRouter(tags=["progress"])


@router.get("/progress/summary", response_model=ProgressSummary)
async def get_progress_summary(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    newly_awarded = await gamification_service.sync_achievements(db, current_user.id)
    xp = await gamification_service.compute_xp(db, current_user.id)
    streak = await gamification_service.compute_streak(db, current_user.id)
    badges = await gamification_service.get_earned_badges(db, current_user.id)
    return ProgressSummary(xp=xp, streak_days=streak, badges=badges, newly_awarded=newly_awarded)


@router.get("/progress/recommendations", response_model=list[SkillRecommendation])
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    rows = await recommendations_service.get_skill_recommendations(db, current_user.id)
    return [SkillRecommendation(**r) for r in rows]


@router.get("/flashcards/due", response_model=list[FlashcardRead])
async def get_due_flashcards(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await flashcard_service.get_due_flashcards(db, current_user.id)


@router.post("/flashcards/{flashcard_id}/review", response_model=FlashcardReviewResult)
async def review_flashcard(
    flashcard_id: uuid.UUID,
    body: FlashcardReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    if not 0 <= body.grade <= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="grade must be 0-5")

    log = await flashcard_service.submit_review(
        db, user_id=current_user.id, flashcard_id=flashcard_id, grade=body.grade
    )
    return FlashcardReviewResult(
        interval_days=log.interval_days, due_at=log.due_at.isoformat(), repetitions=log.repetitions
    )
