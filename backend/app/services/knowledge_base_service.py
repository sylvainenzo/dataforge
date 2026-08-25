from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import GlossaryTerm, Resource


async def list_resources(db: AsyncSession, *, is_free: bool | None = None) -> list[Resource]:
    query = select(Resource).order_by(Resource.title)
    if is_free is not None:
        query = query.where(Resource.is_free == is_free)
    result = await db.execute(query)
    return list(result.scalars().all())


async def list_glossary_terms(db: AsyncSession) -> list[GlossaryTerm]:
    result = await db.execute(select(GlossaryTerm).order_by(GlossaryTerm.term))
    return list(result.scalars().all())


async def get_glossary_term(db: AsyncSession, slug: str) -> GlossaryTerm | None:
    result = await db.execute(select(GlossaryTerm).where(GlossaryTerm.slug == slug))
    return result.scalar_one_or_none()
