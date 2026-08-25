"""The SM-2 algorithm itself is tested in isolation in
test_spaced_repetition.py — these tests cover the API/service layer around
it (app/api/v1/progress.py flashcard endpoints, app/services/
flashcard_service.py), which had zero coverage before this."""

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_flashcard():
    from app.core.db import AsyncSessionLocal
    from app.models.curriculum import Skill
    from app.models.learning_science import Flashcard

    async with AsyncSessionLocal() as db:
        skill = Skill(name="Flashcard Skill", slug="flashcard-skill", category="test")
        db.add(skill)
        await db.flush()

        card = Flashcard(skill_id=skill.id, front="What is 2 + 2?", back="4")
        db.add(card)
        await db.commit()
        return str(card.id)


async def _register_and_login(client, email="flashcard-learner@test.dev"):
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correcthorsebattery", "display_name": "Learner"},
    )


async def test_due_flashcards_requires_auth(client, seeded_flashcard):
    resp = await client.get("/api/v1/flashcards/due")
    assert resp.status_code == 401


async def test_new_flashcard_is_due_before_any_review(client, seeded_flashcard):
    await _register_and_login(client)
    resp = await client.get("/api/v1/flashcards/due")
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert seeded_flashcard in ids


async def test_reviewing_a_flashcard_sets_a_future_due_date(client, seeded_flashcard):
    await _register_and_login(client)

    resp = await client.post(f"/api/v1/flashcards/{seeded_flashcard}/review", json={"grade": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["repetitions"] == 1
    assert body["interval_days"] == 1


async def test_flashcard_is_not_due_immediately_after_a_good_review(client, seeded_flashcard):
    await _register_and_login(client)

    await client.post(f"/api/v1/flashcards/{seeded_flashcard}/review", json={"grade": 5})

    resp = await client.get("/api/v1/flashcards/due")
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert seeded_flashcard not in ids


async def test_review_rejects_out_of_range_grade(client, seeded_flashcard):
    await _register_and_login(client)

    resp = await client.post(f"/api/v1/flashcards/{seeded_flashcard}/review", json={"grade": 9})
    assert resp.status_code == 400


async def test_a_second_review_advances_repetitions(client, seeded_flashcard):
    await _register_and_login(client)

    await client.post(f"/api/v1/flashcards/{seeded_flashcard}/review", json={"grade": 5})
    resp = await client.post(f"/api/v1/flashcards/{seeded_flashcard}/review", json={"grade": 5})
    assert resp.status_code == 200
    assert resp.json()["repetitions"] == 2
    assert resp.json()["interval_days"] == 6
