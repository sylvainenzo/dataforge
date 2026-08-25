"""Skill-gap dashboard recommendations — "what should I practice next" was
previously nothing at all. Completion is computed live from UserProgress,
the same pattern already proven for career-path progress, never a stored
flag that could drift from reality."""

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_skills_and_lessons():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill

    async with AsyncSessionLocal() as db:
        weak_skill = Skill(name="Weak Skill", slug="weak-skill", category="test")
        untouched_skill = Skill(name="Untouched Skill", slug="untouched-skill", category="test")
        mastered_skill = Skill(name="Mastered Skill", slug="mastered-skill", category="test")
        db.add_all([weak_skill, untouched_skill, mastered_skill])
        await db.flush()

        course = Course(title="Rec Test Course", slug="rec-test-course", level=LearningLevel.BEGINNER, published=True)
        db.add(course)
        await db.flush()
        module = Module(course_id=course.id, title="Rec Test Module", slug="rec-test-module", order=1)
        db.add(module)
        await db.flush()

        lessons = {}
        specs = [
            ("weak-1", "Weak Lesson 1", 1, weak_skill),
            ("weak-2", "Weak Lesson 2", 2, weak_skill),
            ("untouched-1", "Untouched Lesson 1", 3, untouched_skill),
            ("mastered-1", "Mastered Lesson 1", 4, mastered_skill),
        ]
        for slug, title, order, skill in specs:
            lesson = Lesson(module_id=module.id, title=title, slug=slug, order=order, content={"blocks": []}, published=True)
            db.add(lesson)
            await db.flush()
            db.add(LessonSkill(lesson_id=lesson.id, skill_id=skill.id))
            lessons[slug] = lesson

        await db.commit()
        return {slug: lesson.slug for slug, lesson in lessons.items()}


async def _register_and_login(client, email="rec-learner@test.dev"):
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "correcthorsebattery", "display_name": "Learner"}
    )


async def test_recommendations_require_auth(client):
    resp = await client.get("/api/v1/progress/recommendations")
    assert resp.status_code == 401


async def test_untouched_skills_recommended_when_nothing_in_progress(client, seeded_skills_and_lessons):
    """Before anything is completed, 'mastered-skill' is just another
    untouched skill (its lesson hasn't been finished yet either) — it only
    becomes exempt once its one lesson is actually marked complete, which
    the next test covers."""

    await _register_and_login(client)
    resp = await client.get("/api/v1/progress/recommendations")
    assert resp.status_code == 200
    slugs = {r["skill_slug"] for r in resp.json()}
    assert "weak-skill" in slugs
    assert "untouched-skill" in slugs
    assert "mastered-skill" in slugs


async def test_in_progress_skill_ranks_above_untouched_and_mastered_is_excluded(client, seeded_skills_and_lessons):
    await _register_and_login(client)

    # Complete one of the two weak-skill lessons (partial progress) and the
    # single mastered-skill lesson (full completion for that skill).
    await client.post("/api/v1/lessons/weak-1/complete")
    await client.post("/api/v1/lessons/mastered-1/complete")

    resp = await client.get("/api/v1/progress/recommendations")
    assert resp.status_code == 200
    body = resp.json()

    slugs = [r["skill_slug"] for r in body]
    assert "mastered-skill" not in slugs  # fully completed — nothing left to recommend

    weak = next(r for r in body if r["skill_slug"] == "weak-skill")
    assert weak["lessons_completed"] == 1
    assert weak["lessons_total"] == 2
    assert weak["completion"] == 0.5
    assert weak["next_lesson"]["slug"] == "weak-2"

    # The in-progress skill (weak-skill, 50%) should be recommended ahead
    # of the untouched one (0%) — it's the more actionable "finish this".
    assert slugs.index("weak-skill") < slugs.index("untouched-skill")
