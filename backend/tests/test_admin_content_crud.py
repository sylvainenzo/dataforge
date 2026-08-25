"""Admin content CRUD (courses/modules/lessons/quizzes) was previously
just a single course-create endpoint. These tests cover the full
create/read/update/delete chain added in app/api/v1/admin.py, including
the regression this surfaced: reading a course tree with a lesson's quiz
attached crashed with a 500 because Quiz.questions wasn't eager-loaded
(see admin_service.get_course_for_admin)."""

import pytest_asyncio


@pytest_asyncio.fixture
async def admin_client(client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import Role, User, UserRole

    await client.post(
        "/api/v1/auth/register",
        json={"email": "admin-tester@test.dev", "password": "correcthorsebattery", "display_name": "Admin"},
    )

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == "admin-tester@test.dev"))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()

    # Re-login so the access token picks up the freshly-granted admin role.
    await client.post(
        "/api/v1/auth/login", json={"email": "admin-tester@test.dev", "password": "correcthorsebattery"}
    )
    return client


async def test_non_admin_cannot_create_course(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "student@test.dev", "password": "correcthorsebattery", "display_name": "Student"},
    )
    resp = await client.post(
        "/api/v1/admin/courses", json={"title": "Should Fail", "level": "beginner", "published": False}
    )
    assert resp.status_code == 403


async def test_full_course_module_lesson_quiz_lifecycle(admin_client):
    create_resp = await admin_client.post(
        "/api/v1/admin/courses",
        json={"title": "Admin CRUD Course", "level": "beginner", "description": "temp", "published": False},
    )
    assert create_resp.status_code == 201
    course_id = create_resp.json()["id"]

    update_resp = await admin_client.patch(f"/api/v1/admin/courses/{course_id}", json={"published": True})
    assert update_resp.status_code == 200
    assert update_resp.json()["published"] is True

    module_resp = await admin_client.post(
        f"/api/v1/admin/courses/{course_id}/modules", json={"title": "Module One", "order": 1}
    )
    assert module_resp.status_code == 201
    module_id = module_resp.json()["id"]

    lesson_resp = await admin_client.post(
        f"/api/v1/admin/modules/{module_id}/lessons",
        json={"title": "Lesson One", "order": 1, "published": True, "content": {"blocks": []}},
    )
    assert lesson_resp.status_code == 201
    lesson_id = lesson_resp.json()["id"]

    quiz_resp = await admin_client.post(
        f"/api/v1/admin/lessons/{lesson_id}/quiz",
        json={
            "title": "Quiz One",
            "passing_score": 70,
            "questions": [
                {
                    "question_text": "2 + 2?",
                    "question_type": "multiple_choice",
                    "options": {"choices": ["3", "4"]},
                    "correct_answer": {"value": "4"},
                    "order": 1,
                    "points": 1,
                }
            ],
        },
    )
    assert quiz_resp.status_code == 201
    quiz_id = quiz_resp.json()["id"]
    assert len(quiz_resp.json()["questions"]) == 1

    # This is the regression check: reading the full tree with a quiz
    # attached must not 500 (Quiz.questions needs to be eager-loaded).
    tree_resp = await admin_client.get(f"/api/v1/admin/courses/{course_id}")
    assert tree_resp.status_code == 200
    tree = tree_resp.json()
    assert tree["modules"][0]["lessons"][0]["quiz"]["title"] == "Quiz One"
    assert len(tree["modules"][0]["lessons"][0]["quiz"]["questions"]) == 1

    await admin_client.delete(f"/api/v1/admin/quizzes/{quiz_id}")
    await admin_client.delete(f"/api/v1/admin/lessons/{lesson_id}")
    await admin_client.delete(f"/api/v1/admin/modules/{module_id}")
    delete_course_resp = await admin_client.delete(f"/api/v1/admin/courses/{course_id}")
    assert delete_course_resp.status_code == 204

    final_get = await admin_client.get(f"/api/v1/admin/courses/{course_id}")
    assert final_get.status_code == 404


async def test_duplicate_module_order_returns_409(admin_client):
    course_resp = await admin_client.post(
        "/api/v1/admin/courses", json={"title": "Order Conflict Course", "level": "beginner", "published": False}
    )
    course_id = course_resp.json()["id"]

    await admin_client.post(f"/api/v1/admin/courses/{course_id}/modules", json={"title": "First", "order": 1})
    dup_resp = await admin_client.post(f"/api/v1/admin/courses/{course_id}/modules", json={"title": "Dup", "order": 1})
    assert dup_resp.status_code == 409


async def test_admin_can_grant_and_revoke_instructor_role(admin_client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import User

    async with AsyncSessionLocal() as db:
        target = (await db.execute(select(User).where(User.email == "admin-tester@test.dev"))).scalar_one()

    grant_resp = await admin_client.patch(
        f"/api/v1/admin/users/{target.id}/role", json={"role": "instructor", "grant": True}
    )
    assert grant_resp.status_code == 204

    users_resp = await admin_client.get("/api/v1/admin/users")
    roles = next(u["roles"] for u in users_resp.json() if u["email"] == "admin-tester@test.dev")
    assert "instructor" in roles
