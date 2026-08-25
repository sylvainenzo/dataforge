"""Project submission flow — the ProjectSubmission model existed with zero
rows and zero API surface before this. Covers the student-facing submit
path and the admin review queue added in app/api/v1/projects.py and
app/api/v1/admin.py."""

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_project():
    from app.core.db import AsyncSessionLocal
    from app.models.base import DifficultyLevel
    from app.models.projects import Project, ProjectType

    async with AsyncSessionLocal() as db:
        project = Project(
            title="Submission Test Project",
            slug="submission-test-project",
            description="A project for testing the submission flow.",
            difficulty=DifficultyLevel.BEGINNER,
            project_type=ProjectType.EDA,
            rubric={},
        )
        db.add(project)
        await db.commit()
        return project.slug


async def _register_and_login(client, email="submitter@test.dev"):
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "correcthorsebattery", "display_name": "Submitter"}
    )


@pytest_asyncio.fixture
async def admin_client(client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import Role, User, UserRole

    await client.post(
        "/api/v1/auth/register",
        json={"email": "submission-admin@test.dev", "password": "correcthorsebattery", "display_name": "Admin"},
    )
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == "submission-admin@test.dev"))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()
    await client.post(
        "/api/v1/auth/login", json={"email": "submission-admin@test.dev", "password": "correcthorsebattery"}
    )
    return client


async def test_submit_requires_auth(client, seeded_project):
    resp = await client.post(
        f"/api/v1/projects/{seeded_project}/submissions", json={"submission_url": "https://github.com/x/y"}
    )
    assert resp.status_code == 401


async def test_submit_and_list_own_submissions(client, seeded_project):
    await _register_and_login(client)

    submit_resp = await client.post(
        f"/api/v1/projects/{seeded_project}/submissions", json={"submission_url": "https://github.com/x/y"}
    )
    assert submit_resp.status_code == 201
    body = submit_resp.json()
    assert body["status"] == "submitted"
    assert body["submission_url"] == "https://github.com/x/y"
    assert body["feedback"] is None

    list_resp = await client.get(f"/api/v1/projects/{seeded_project}/submissions")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


async def test_submit_to_unknown_project_404s(client):
    await _register_and_login(client)
    resp = await client.post("/api/v1/projects/does-not-exist/submissions", json={"submission_url": "https://x.com"})
    assert resp.status_code == 404


async def test_admin_can_see_and_review_submission(admin_client, seeded_project, client):
    # admin_client and client share one cookie jar (same underlying
    # AsyncClient) — registering a second user overwrites whichever
    # session was active, so re-login as admin below before using
    # admin-only endpoints again.
    await client.post(
        "/api/v1/auth/register",
        json={"email": "another-submitter@test.dev", "password": "correcthorsebattery", "display_name": "S"},
    )
    submit_resp = await client.post(
        f"/api/v1/projects/{seeded_project}/submissions", json={"submission_url": "https://github.com/a/b"}
    )
    submission_id = submit_resp.json()["id"]

    await client.post(
        "/api/v1/auth/login", json={"email": "submission-admin@test.dev", "password": "correcthorsebattery"}
    )

    list_resp = await admin_client.get("/api/v1/admin/project-submissions")
    assert list_resp.status_code == 200
    row = next(r for r in list_resp.json() if r["id"] == submission_id)
    assert row["project_title"] == "Submission Test Project"
    assert row["user_email"] == "another-submitter@test.dev"
    assert row["status"] == "submitted"

    review_resp = await admin_client.patch(
        f"/api/v1/admin/project-submissions/{submission_id}",
        json={"status": "passed", "feedback": "Nice work — clear write-up."},
    )
    assert review_resp.status_code == 200
    reviewed = review_resp.json()
    assert reviewed["status"] == "passed"
    assert reviewed["feedback"] == "Nice work — clear write-up."
    assert reviewed["reviewed_at"] is not None


async def test_non_admin_cannot_review_submissions(client, seeded_project):
    await _register_and_login(client)
    resp = await client.get("/api/v1/admin/project-submissions")
    assert resp.status_code == 403
