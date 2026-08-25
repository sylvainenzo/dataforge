"""Resources and Glossary were a model with zero API surface until this
feature was built — these tests cover the read paths added in
app/api/v1/knowledge_base.py."""

from datetime import date

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_resources():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.knowledge_base import GlossaryTerm, Resource

    async with AsyncSessionLocal() as db:
        db.add(
            Resource(
                title="Free Resource",
                provider="Test Provider",
                level=LearningLevel.BEGINNER,
                is_free=True,
                description="A free one.",
                url="https://example.com/free",
                last_verified_at=date(2026, 1, 1),
            )
        )
        db.add(
            Resource(
                title="Paid Resource",
                provider="Test Provider",
                level=LearningLevel.ADVANCED,
                is_free=False,
                description="A paid one.",
                url="https://example.com/paid",
                last_verified_at=date(2026, 1, 1),
            )
        )
        db.add(
            GlossaryTerm(
                term="Test Term",
                slug="test-term",
                simple_explanation="A simple explanation.",
                technical_explanation="A technical one.",
                example="example()",
            )
        )
        await db.commit()


async def test_list_resources_returns_all(client, seeded_resources):
    resp = await client.get("/api/v1/resources")
    assert resp.status_code == 200
    titles = {r["title"] for r in resp.json()}
    assert titles == {"Free Resource", "Paid Resource"}


async def test_list_resources_filters_by_is_free(client, seeded_resources):
    resp = await client.get("/api/v1/resources", params={"is_free": "true"})
    assert resp.status_code == 200
    titles = {r["title"] for r in resp.json()}
    assert titles == {"Free Resource"}


async def test_list_glossary_terms(client, seeded_resources):
    resp = await client.get("/api/v1/glossary")
    assert resp.status_code == 200
    terms = resp.json()
    assert len(terms) == 1
    assert terms[0]["term"] == "Test Term"


async def test_get_glossary_term_by_slug(client, seeded_resources):
    resp = await client.get("/api/v1/glossary/test-term")
    assert resp.status_code == 200
    assert resp.json()["simple_explanation"] == "A simple explanation."


async def test_get_glossary_term_404_for_unknown_slug(client, seeded_resources):
    resp = await client.get("/api/v1/glossary/does-not-exist")
    assert resp.status_code == 404
