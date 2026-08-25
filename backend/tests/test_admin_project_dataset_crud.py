"""Admin CRUD for projects and dataset metadata — projects previously had
no admin write path at all; datasets could only be created via user
upload, with no admin edit/delete."""

import pytest_asyncio


@pytest_asyncio.fixture
async def admin_client(client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import Role, User, UserRole

    await client.post(
        "/api/v1/auth/register",
        json={"email": "pd-admin@test.dev", "password": "correcthorsebattery", "display_name": "Admin"},
    )
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == "pd-admin@test.dev"))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()
    await client.post("/api/v1/auth/login", json={"email": "pd-admin@test.dev", "password": "correcthorsebattery"})
    return client


@pytest_asyncio.fixture
async def seeded_dataset():
    from datetime import date

    from app.core.db import AsyncSessionLocal
    from app.models.base import DifficultyLevel
    from app.models.datasets import Dataset, DatasetFormat

    async with AsyncSessionLocal() as db:
        dataset = Dataset(
            name="Admin CRUD Test Dataset",
            slug="admin-crud-test-dataset",
            description="original description",
            source="Test",
            source_url="internal://test",
            license="Test license",
            domain="Test",
            difficulty=DifficultyLevel.BEGINNER,
            format=DatasetFormat.CSV,
        )
        db.add(dataset)
        await db.commit()
        return str(dataset.id)


async def test_project_full_crud(admin_client):
    create_resp = await admin_client.post(
        "/api/v1/admin/projects",
        json={
            "title": "Admin CRUD Project",
            "description": "A project created via admin CRUD.",
            "difficulty": "beginner",
            "project_type": "eda",
            "rubric": {"objectives": ["Learn something"]},
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    project_id = body["id"]
    assert body["slug"] == "admin-crud-project"

    update_resp = await admin_client.patch(
        f"/api/v1/admin/projects/{project_id}", json={"description": "Updated description."}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Updated description."

    list_resp = await admin_client.get("/api/v1/admin/projects")
    assert any(p["id"] == project_id for p in list_resp.json())

    # Confirm it's visible through the public, read-only projects endpoint too.
    public_resp = await admin_client.get("/api/v1/projects/admin-crud-project")
    assert public_resp.status_code == 200

    delete_resp = await admin_client.delete(f"/api/v1/admin/projects/{project_id}")
    assert delete_resp.status_code == 204

    public_after = await admin_client.get("/api/v1/projects/admin-crud-project")
    assert public_after.status_code == 404


async def test_non_admin_cannot_create_project(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "pd-student@test.dev", "password": "correcthorsebattery", "display_name": "S"},
    )
    resp = await client.post(
        "/api/v1/admin/projects",
        json={"title": "Should fail", "description": "x", "difficulty": "beginner", "project_type": "eda"},
    )
    assert resp.status_code == 403


async def test_dataset_update_and_delete(admin_client, seeded_dataset):
    update_resp = await admin_client.patch(
        f"/api/v1/admin/datasets/{seeded_dataset}", json={"description": "updated via admin"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "updated via admin"

    list_resp = await admin_client.get("/api/v1/admin/datasets")
    assert any(d["id"] == seeded_dataset for d in list_resp.json())

    delete_resp = await admin_client.delete(f"/api/v1/admin/datasets/{seeded_dataset}")
    assert delete_resp.status_code == 204

    list_after = await admin_client.get("/api/v1/admin/datasets")
    assert not any(d["id"] == seeded_dataset for d in list_after.json())
