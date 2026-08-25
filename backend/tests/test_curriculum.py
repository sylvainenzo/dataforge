"""Includes a regression test for a real bug found during Phase 11
development: re-visiting an already-completed lesson silently downgraded
its status back to in-progress. See app/services/curriculum_service.py's
mark_lesson_progress for the fix."""

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_lesson():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.curriculum import Course, Lesson, Module

    async with AsyncSessionLocal() as db:
        course = Course(title="Test Course", slug="test-course", level=LearningLevel.BEGINNER, published=True)
        db.add(course)
        await db.flush()

        module = Module(course_id=course.id, title="Test Module", slug="test-module", order=1)
        db.add(module)
        await db.flush()

        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            slug="test-lesson",
            order=1,
            content={"blocks": []},
            published=True,
        )
        db.add(lesson)
        await db.commit()
        return lesson.slug


async def _register_and_login(client, email="learner@test.dev"):
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correcthorsebattery", "display_name": "Learner"},
    )


async def test_completing_a_lesson_marks_it_complete(client, seeded_lesson):
    await _register_and_login(client)

    complete_resp = await client.post(f"/api/v1/lessons/{seeded_lesson}/complete")
    assert complete_resp.status_code == 204


async def test_revisiting_a_completed_lesson_does_not_downgrade_it(client, seeded_lesson):
    """Regression test — this exact sequence (complete, then re-view)
    previously reset status back to in_progress and progress_percent to 50."""

    await _register_and_login(client)

    await client.post(f"/api/v1/lessons/{seeded_lesson}/complete")

    # Re-viewing the lesson calls GET, which used to unconditionally mark
    # in_progress regardless of existing state.
    view_resp = await client.get(f"/api/v1/lessons/{seeded_lesson}")
    assert view_resp.status_code == 200

    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.learning_science import ProgressStatus, UserProgress

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(UserProgress).where(UserProgress.lesson_id.is_not(None)))
        row = result.scalar_one()
        assert row.status == ProgressStatus.COMPLETED
        assert row.progress_percent == 100


async def test_viewing_lesson_first_marks_in_progress(client, seeded_lesson):
    await _register_and_login(client)

    resp = await client.get(f"/api/v1/lessons/{seeded_lesson}")
    assert resp.status_code == 200

    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.learning_science import ProgressStatus, UserProgress

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(UserProgress).where(UserProgress.lesson_id.is_not(None)))
        row = result.scalar_one()
        assert row.status == ProgressStatus.IN_PROGRESS
