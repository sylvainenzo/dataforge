from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.search import SearchResult

# Real Postgres full-text search (Phase 1 §14's recommendation), computed
# on the fly with to_tsvector/plainto_tsquery rather than a stored,
# GIN-indexed column — fine at today's content volume; the documented
# upgrade path if it ever needs to scale is a generated tsvector column
# with a GIN index, not a different query shape. `:q` is always bound as a
# parameter, never string-interpolated, so this is not injectable.
SEARCH_SQL = text(
    """
    SELECT 'course' AS type, title, description AS subtitle, slug, NULL AS external_url,
           ts_rank(to_tsvector('english', title || ' ' || coalesce(description, '')), plainto_tsquery('english', :q)) AS rank
    FROM courses
    WHERE published = true
      AND to_tsvector('english', title || ' ' || coalesce(description, '')) @@ plainto_tsquery('english', :q)

    UNION ALL

    SELECT 'lesson', title, NULL, slug, NULL,
           ts_rank(to_tsvector('english', title), plainto_tsquery('english', :q))
    FROM lessons
    WHERE published = true
      AND to_tsvector('english', title) @@ plainto_tsquery('english', :q)

    UNION ALL

    SELECT 'tool', name, description, slug, NULL,
           ts_rank(to_tsvector('english', name || ' ' || description), plainto_tsquery('english', :q))
    FROM tools
    WHERE to_tsvector('english', name || ' ' || description) @@ plainto_tsquery('english', :q)

    UNION ALL

    SELECT 'project', title, description, slug, NULL,
           ts_rank(to_tsvector('english', title || ' ' || description), plainto_tsquery('english', :q))
    FROM projects
    WHERE to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', :q)

    UNION ALL

    SELECT 'resource', title, description, NULL, url,
           ts_rank(to_tsvector('english', title || ' ' || coalesce(description, '')), plainto_tsquery('english', :q))
    FROM resources
    WHERE to_tsvector('english', title || ' ' || coalesce(description, '')) @@ plainto_tsquery('english', :q)

    UNION ALL

    SELECT 'glossary_term', term, simple_explanation, slug, NULL,
           ts_rank(to_tsvector('english', term || ' ' || simple_explanation), plainto_tsquery('english', :q))
    FROM glossary_terms
    WHERE to_tsvector('english', term || ' ' || simple_explanation) @@ plainto_tsquery('english', :q)

    ORDER BY rank DESC
    LIMIT :limit
    """
)


async def search(db: AsyncSession, query: str, limit: int = 20) -> list[SearchResult]:
    query = query.strip()
    if not query:
        return []

    result = await db.execute(SEARCH_SQL, {"q": query, "limit": limit})
    return [
        SearchResult(type=row.type, title=row.title, subtitle=row.subtitle, slug=row.slug, external_url=row.external_url)
        for row in result
    ]
