from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.knowledge_base import GlossaryTermRead, ResourceRead
from app.services import knowledge_base_service

router = APIRouter(tags=["resources"])


@router.get("/resources", response_model=list[ResourceRead])
async def list_resources(is_free: bool | None = None, db: AsyncSession = Depends(get_db)):
    return await knowledge_base_service.list_resources(db, is_free=is_free)


@router.get("/glossary", response_model=list[GlossaryTermRead])
async def list_glossary_terms(db: AsyncSession = Depends(get_db)):
    return await knowledge_base_service.list_glossary_terms(db)


@router.get("/glossary/{slug}", response_model=GlossaryTermRead)
async def get_glossary_term(slug: str, db: AsyncSession = Depends(get_db)):
    term = await knowledge_base_service.get_glossary_term(db, slug)
    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossary term not found")
    return term
