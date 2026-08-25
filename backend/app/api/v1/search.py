from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.search import SearchResult
from app.services import search_service

router = APIRouter(tags=["search"])


@router.get("/search", response_model=list[SearchResult])
async def search(q: str = "", db: AsyncSession = Depends(get_db)):
    return await search_service.search(db, q)
