"""Career paths were a model with zero API surface until this feature was
built. The progress endpoint is the one worth guarding carefully: it must
be derived from real completed-lesson activity, never a stored counter —
test_progress_reflects_completed_lessons is the regression test for that."""

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_career_path():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.career import CareerPath, CareerPathSkill
    from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill

    async with AsyncSessionLocal() as db:
        skill = Skill(name="Test Skill", slug="test-skill", category="test")
        db.add(skill)
        await db.flush()

        career_path = CareerPath(name="Test Analyst", slug="test-analyst", description="A test career path.")
        db.add(career_path)
        await db.flush()

        db.add(CareerPathSkill(career_path_id=career_path.id, skill_id=skill.id, weight=2.0))

        course = Course(title="Test Course", slug="career-test-course", level=LearningLevel.BEGINNER, published=True)
        db.add(course)
        await db.flush()
        module = Module(course_id=course.id, title="Test Module", slug="career-test-module", order=1)
        db.add(module)
        await db.flush()

        lesson_a = Lesson(module_id=module.id, title="Lesson A", slug="career-lesson-a", order=1, content={"blocks": []}, published=True)
        lesson_b = Lesson(module_id=module.id, title="Lesson B", slug="career-lesson-b", order=2, content={"blocks": []}, published=True)
        db.add_all([lesson_a, lesson_b])
        await db.flush()

        db.add_all(
            [
                LessonSkill(lesson_id=lesson_a.id, skill_id=skill.id),
                LessonSkill(lesson_id=lesson_b.id, skill_id=skill.id),
            ]
        )
        await db.commit()
        return {"career_path_slug": career_path.slug, "lesson_a_slug": lesson_a.slug, "lesson_b_slug": lesson_b.slug}


async def _register_and_login(client, email="career-learner@test.dev"):
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correcthorsebattery", "display_name": "Learner"},
    )


async def test_list_career_paths(client, seeded_career_path):
    resp = await client.get("/api/v1/career-paths")
    assert resp.status_code == 200
    slugs = {p["slug"] for p in resp.json()}
    assert "test-analyst" in slugs


async def test_get_career_path_detail_includes_weighted_skill(client, seeded_career_path):
    resp = await client.get("/api/v1/career-paths/test-analyst")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["skills"]) == 1
    assert body["skills"][0]["skill_slug"] == "test-skill"
    assert body["skills"][0]["weight"] == 2.0


async def test_unknown_career_path_404(client, seeded_career_path):
    resp = await client.get("/api/v1/career-paths/does-not-exist")
    assert resp.status_code == 404


async def test_progress_requires_auth(client, seeded_career_path):
    resp = await client.get("/api/v1/career-paths/test-analyst/progress")
    assert resp.status_code == 401


async def test_progress_starts_at_zero(client, seeded_career_path):
    await _register_and_login(client)
    resp = await client.get("/api/v1/career-paths/test-analyst/progress")
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_completion"] == 0
    assert body["skills"][0]["lessons_completed"] == 0
    assert body["skills"][0]["lessons_total"] == 2


async def test_progress_reflects_completed_lessons(client, seeded_career_path):
    """The core guarantee: progress is computed live from UserProgress, so
    completing a lesson moves the number without any separate write to a
    career-progress table (there isn't one)."""

    await _register_and_login(client)

    await client.post(f"/api/v1/lessons/{seeded_career_path['lesson_a_slug']}/complete")

    resp = await client.get("/api/v1/career-paths/test-analyst/progress")
    assert resp.status_code == 200
    body = resp.json()
    assert body["skills"][0]["lessons_completed"] == 1
    assert body["skills"][0]["completion"] == 0.5
    assert body["overall_completion"] == 0.5

    await client.post(f"/api/v1/lessons/{seeded_career_path['lesson_b_slug']}/complete")

    resp2 = await client.get("/api/v1/career-paths/test-analyst/progress")
    body2 = resp2.json()
    assert body2["skills"][0]["lessons_completed"] == 2
    assert body2["overall_completion"] == 1.0
