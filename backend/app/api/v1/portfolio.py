import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.schemas.portfolio import PortfolioSettings, PortfolioSettingsUpdate, PublicPortfolio
from app.services import portfolio_service

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio/settings", response_model=PortfolioSettings)
async def get_portfolio_settings(
    db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    profile = await portfolio_service.get_portfolio_settings(db, current_user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.patch("/portfolio/settings", response_model=PortfolioSettings)
async def update_portfolio_settings(
    body: PortfolioSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await portfolio_service.update_portfolio_settings(db, current_user.id, **body.model_dump())


@router.get("/portfolio/{user_id}", response_model=PublicPortfolio)
async def get_public_portfolio(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await portfolio_service.get_public_portfolio(db, user_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return result
