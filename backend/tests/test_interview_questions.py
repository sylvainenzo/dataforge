"""Interview question bank — public browse/filter endpoints plus admin CRUD
(P2 roadmap item)."""

import pytest_asyncio


@pytest_asyncio.fixture
async def admin_client(client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import Role, User, UserRole

    await client.post(
        "/api/v1/auth/register",
        json={"email": "iq-admin@test.dev", "password": "correcthorsebattery", "display_name": "Admin"},
    )

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == "iq-admin@test.dev"))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()

    await client.post("/api/v1/auth/login", json={"email": "iq-admin@test.dev", "password": "correcthorsebattery"})
    return client


@pytest_asyncio.fixture
async def seeded_career_path():
    from app.core.db import AsyncSessionLocal
    from app.models.career import CareerPath

    async with AsyncSessionLocal() as db:
        career_path = CareerPath(name="IQ Test Career", slug="iq-test-career")
        db.add(career_path)
        await db.commit()
        return career_path.id, career_path.slug


async def test_list_interview_questions_is_public(client):
    resp = await client.get("/api/v1/interview-questions")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_filter_by_category_and_difficulty(admin_client):
    await admin_client.post(
        "/api/v1/admin/interview-questions",
        json={
            "question": "Filter test question?",
            "category": "FilterCategory",
            "difficulty": "advanced",
            "sample_answer": "Filter test answer.",
        },
    )

    resp = await admin_client.get("/api/v1/interview-questions", params={"category": "FilterCategory"})
    assert resp.status_code == 200
    assert all(q["category"] == "FilterCategory" for q in resp.json())
    assert any(q["question"] == "Filter test question?" for q in resp.json())

    resp_diff = await admin_client.get("/api/v1/interview-questions", params={"difficulty": "advanced"})
    assert all(q["difficulty"] == "advanced" for q in resp_diff.json())

    resp_none = await admin_client.get("/api/v1/interview-questions", params={"category": "NoSuchCategory"})
    assert resp_none.json() == []


async def test_filter_by_career_path(admin_client, seeded_career_path):
    career_path_id, career_path_slug = seeded_career_path
    await admin_client.post(
        "/api/v1/admin/interview-questions",
        json={
            "question": "Career-scoped question?",
            "category": "CareerFilter",
            "difficulty": "technical",
            "sample_answer": "Career-scoped answer.",
            "career_path_id": str(career_path_id),
        },
    )

    resp = await admin_client.get("/api/v1/interview-questions", params={"career_path": career_path_slug})
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 1
    assert questions[0]["question"] == "Career-scoped question?"


async def test_list_categories(admin_client):
    await admin_client.post(
        "/api/v1/admin/interview-questions",
        json={
            "question": "Category listing question?",
            "category": "UniqueCategoryXYZ",
            "difficulty": "beginner",
            "sample_answer": "Answer.",
        },
    )
    resp = await admin_client.get("/api/v1/interview-questions/categories")
    assert resp.status_code == 200
    assert "UniqueCategoryXYZ" in resp.json()


async def test_admin_interview_question_full_crud(admin_client):
    create_resp = await admin_client.post(
        "/api/v1/admin/interview-questions",
        json={
            "question": "Admin CRUD question?",
            "category": "AdminCRUD",
            "difficulty": "practical",
            "sample_answer": "Admin CRUD answer.",
        },
    )
    assert create_resp.status_code == 201
    question_id = create_resp.json()["id"]

    update_resp = await admin_client.patch(
        f"/api/v1/admin/interview-questions/{question_id}", json={"sample_answer": "Updated answer."}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["sample_answer"] == "Updated answer."

    list_resp = await admin_client.get("/api/v1/admin/interview-questions")
    assert any(q["id"] == question_id for q in list_resp.json())

    delete_resp = await admin_client.delete(f"/api/v1/admin/interview-questions/{question_id}")
    assert delete_resp.status_code == 204

    list_after = await admin_client.get("/api/v1/admin/interview-questions")
    assert not any(q["id"] == question_id for q in list_after.json())


async def test_update_nonexistent_interview_question_404s(admin_client):
    import uuid

    resp = await admin_client.patch(
        f"/api/v1/admin/interview-questions/{uuid.uuid4()}", json={"sample_answer": "x"}
    )
    assert resp.status_code == 404


async def test_non_admin_cannot_manage_interview_questions(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "iq-student@test.dev", "password": "correcthorsebattery", "display_name": "Student"},
    )
    resp = await client.post(
        "/api/v1/admin/interview-questions",
        json={
            "question": "Should fail?",
            "category": "X",
            "difficulty": "beginner",
            "sample_answer": "x",
        },
    )
    assert resp.status_code == 403
