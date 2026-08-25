"""The CommandPalette was explicitly a cosmetic shell with no backend
before this — these tests cover app/services/search_service.py's real
Postgres full-text search across courses, lessons, tools, projects,
resources, and glossary terms."""

from datetime import date

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_search_content():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.curriculum import Course
    from app.models.knowledge_base import GlossaryTerm, Resource

    async with AsyncSessionLocal() as db:
        db.add(
            Course(
                title="Searchable Widgets 101",
                slug="searchable-widgets-101",
                description="An introduction to widget theory.",
                level=LearningLevel.BEGINNER,
                published=True,
            )
        )
        db.add(
            Course(
                title="Unpublished Widgets",
                slug="unpublished-widgets",
                description="Should never appear in search results.",
                level=LearningLevel.BEGINNER,
                published=False,
            )
        )
        db.add(
            Resource(
                title="Widget Reference Guide",
                provider="Test",
                level=LearningLevel.BEGINNER,
                is_free=True,
                description="Everything about widgets.",
                url="https://example.com/widgets",
                last_verified_at=date(2026, 1, 1),
            )
        )
        db.add(
            GlossaryTerm(
                term="Widget",
                slug="widget",
                simple_explanation="A small reusable thing.",
            )
        )
        await db.commit()


async def test_search_finds_matches_across_content_types(client, seeded_search_content):
    resp = await client.get("/api/v1/search", params={"q": "widget"})
    assert resp.status_code == 200
    body = resp.json()
    types = {r["type"] for r in body}
    assert types == {"course", "resource", "glossary_term"}


async def test_search_excludes_unpublished_courses(client, seeded_search_content):
    resp = await client.get("/api/v1/search", params={"q": "widget"})
    titles = {r["title"] for r in resp.json()}
    assert "Unpublished Widgets" not in titles
    assert "Searchable Widgets 101" in titles


async def test_search_returns_empty_list_for_no_match(client, seeded_search_content):
    resp = await client.get("/api/v1/search", params={"q": "nonexistentxyzterm"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_search_returns_empty_list_for_blank_query(client, seeded_search_content):
    resp = await client.get("/api/v1/search", params={"q": ""})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_search_query_is_not_injectable(client, seeded_search_content):
    resp = await client.get("/api/v1/search", params={"q": "'; DROP TABLE courses; --"})
    assert resp.status_code == 200

    verify = await client.get("/api/v1/search", params={"q": "widget"})
    assert len(verify.json()) > 0
