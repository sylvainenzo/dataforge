"""Admin CRUD for resources, glossary terms, tools, and career paths — these
content types previously only had GET endpoints (or none at all) and had to
be edited via one-off seed scripts. Covers the create/update/delete surface
added in app/api/v1/admin.py this session."""

import pytest_asyncio


@pytest_asyncio.fixture
async def admin_client(client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import Role, User, UserRole

    await client.post(
        "/api/v1/auth/register",
        json={"email": "kc-admin@test.dev", "password": "correcthorsebattery", "display_name": "Admin"},
    )

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == "kc-admin@test.dev"))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()

    await client.post("/api/v1/auth/login", json={"email": "kc-admin@test.dev", "password": "correcthorsebattery"})
    return client


@pytest_asyncio.fixture
async def seeded_skill():
    from app.core.db import AsyncSessionLocal
    from app.models.curriculum import Skill

    async with AsyncSessionLocal() as db:
        skill = Skill(name="Admin Test Skill", slug="admin-test-skill", category="test")
        db.add(skill)
        await db.commit()
        return skill.slug


async def test_resource_full_crud(admin_client):
    create_resp = await admin_client.post(
        "/api/v1/admin/resources",
        json={
            "title": "Admin CRUD Resource",
            "provider": "Test",
            "level": "beginner",
            "is_free": True,
            "url": "https://example.com/admin-crud",
            "last_verified_at": "2026-08-25",
        },
    )
    assert create_resp.status_code == 201
    resource_id = create_resp.json()["id"]

    update_resp = await admin_client.patch(
        f"/api/v1/admin/resources/{resource_id}", json={"title": "Updated Title"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Title"

    list_resp = await admin_client.get("/api/v1/admin/resources")
    assert any(r["id"] == resource_id for r in list_resp.json())

    delete_resp = await admin_client.delete(f"/api/v1/admin/resources/{resource_id}")
    assert delete_resp.status_code == 204

    list_after = await admin_client.get("/api/v1/admin/resources")
    assert not any(r["id"] == resource_id for r in list_after.json())


async def test_glossary_term_full_crud(admin_client):
    create_resp = await admin_client.post(
        "/api/v1/admin/glossary",
        json={"term": "Admin Test Term", "simple_explanation": "A term added via admin CRUD."},
    )
    assert create_resp.status_code == 201
    term_id = create_resp.json()["id"]
    assert create_resp.json()["slug"] == "admin-test-term"

    update_resp = await admin_client.patch(
        f"/api/v1/admin/glossary/{term_id}", json={"simple_explanation": "Updated explanation."}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["simple_explanation"] == "Updated explanation."

    delete_resp = await admin_client.delete(f"/api/v1/admin/glossary/{term_id}")
    assert delete_resp.status_code == 204


async def test_tool_full_crud(admin_client):
    create_resp = await admin_client.post(
        "/api/v1/admin/tools",
        json={
            "name": "Admin CRUD Tool",
            "description": "A tool added via admin CRUD.",
            "category": "testing",
            "official_url": "https://example.com/tool",
            "mac_supported": True,
            "apple_silicon_supported": True,
            "intel_supported": True,
            "install_method": "brew",
            "last_verified_at": "2026-08-25",
        },
    )
    assert create_resp.status_code == 201
    tool_id = create_resp.json()["id"]
    assert create_resp.json()["slug"] == "admin-crud-tool"

    update_resp = await admin_client.patch(
        f"/api/v1/admin/tools/{tool_id}", json={"description": "Updated tool description."}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Updated tool description."

    delete_resp = await admin_client.delete(f"/api/v1/admin/tools/{tool_id}")
    assert delete_resp.status_code == 204


async def test_career_path_full_crud_with_skill_weights(admin_client, seeded_skill):
    create_resp = await admin_client.post(
        "/api/v1/admin/career-paths",
        json={
            "name": "Admin CRUD Career",
            "description": "A career path added via admin CRUD.",
            "skill_weights": {seeded_skill: 2.0},
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    career_path_id = body["id"]
    assert body["skill_weights"] == {seeded_skill: 2.0}

    update_resp = await admin_client.patch(
        f"/api/v1/admin/career-paths/{career_path_id}", json={"skill_weights": {seeded_skill: 3.5}}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["skill_weights"] == {seeded_skill: 3.5}
    # Regression guard: this schema must never leak an unrelated `modules`
    # field (a copy-paste artifact from AdminCourseRead found this session).
    assert "modules" not in update_resp.json()

    # Confirm this is reflected in the public career-path detail endpoint too.
    public_detail = await admin_client.get("/api/v1/career-paths/admin-crud-career")
    assert public_detail.status_code == 200
    assert public_detail.json()["skills"][0]["weight"] == 3.5

    delete_resp = await admin_client.delete(f"/api/v1/admin/career-paths/{career_path_id}")
    assert delete_resp.status_code == 204


async def test_non_admin_cannot_manage_knowledge_base(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "kc-student@test.dev", "password": "correcthorsebattery", "display_name": "Student"},
    )
    resp = await client.post(
        "/api/v1/admin/resources",
        json={
            "title": "Should fail",
            "provider": "Test",
            "level": "beginner",
            "is_free": True,
            "url": "https://example.com/x",
            "last_verified_at": "2026-08-25",
        },
    )
    assert resp.status_code == 403
