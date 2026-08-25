"""Portfolio builder (P2 roadmap item) — an opt-in public page showing a
learner's passed project submissions and issued certificates, built from
real activity (never fabricated or manually curated data)."""

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_project():
    from app.core.db import AsyncSessionLocal
    from app.models.base import DifficultyLevel
    from app.models.projects import Project, ProjectType

    async with AsyncSessionLocal() as db:
        project = Project(
            title="Portfolio Test Project",
            slug="portfolio-test-project",
            description="A project for testing the portfolio builder.",
            difficulty=DifficultyLevel.BEGINNER,
            project_type=ProjectType.EDA,
            rubric={},
        )
        db.add(project)
        await db.commit()
        return project.slug


@pytest_asyncio.fixture
async def seeded_course_with_lessons():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.curriculum import Course, Lesson, Module

    async with AsyncSessionLocal() as db:
        course = Course(
            title="Portfolio Test Course", slug="portfolio-test-course", level=LearningLevel.BEGINNER, published=True
        )
        db.add(course)
        await db.flush()
        module = Module(course_id=course.id, title="Module", slug="portfolio-test-module", order=1)
        db.add(module)
        await db.flush()
        db.add(
            Lesson(
                module_id=module.id, title="Lesson", slug="portfolio-test-lesson", order=1,
                content={"blocks": []}, published=True,
            )
        )
        await db.commit()
        return course.slug


@pytest_asyncio.fixture
async def admin_client(client):
    from sqlalchemy import select

    from app.core.db import AsyncSessionLocal
    from app.models.identity import Role, User, UserRole

    await client.post(
        "/api/v1/auth/register",
        json={"email": "portfolio-admin@test.dev", "password": "correcthorsebattery", "display_name": "Admin"},
    )
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == "portfolio-admin@test.dev"))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        await db.commit()
    await client.post(
        "/api/v1/auth/login", json={"email": "portfolio-admin@test.dev", "password": "correcthorsebattery"}
    )
    return client


async def _register_and_login(client, email="portfolio-learner@test.dev"):
    resp = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "correcthorsebattery", "display_name": "Learner"}
    )
    return resp.json()["id"]


async def test_settings_require_auth(client):
    resp = await client.get("/api/v1/portfolio/settings")
    assert resp.status_code == 401


async def test_default_settings_are_private_with_no_bio(client):
    await _register_and_login(client)
    resp = await client.get("/api/v1/portfolio/settings")
    assert resp.status_code == 200
    assert resp.json() == {"bio": None, "portfolio_public": False}


async def test_update_settings(client):
    await _register_and_login(client)
    resp = await client.patch(
        "/api/v1/portfolio/settings", json={"bio": "Aspiring data analyst.", "portfolio_public": True}
    )
    assert resp.status_code == 200
    assert resp.json() == {"bio": "Aspiring data analyst.", "portfolio_public": True}


async def test_public_portfolio_404s_when_not_made_public(client):
    user_id = await _register_and_login(client)
    resp = await client.get(f"/api/v1/portfolio/{user_id}")
    assert resp.status_code == 404


async def test_public_portfolio_404s_for_unknown_user(client):
    import uuid

    resp = await client.get(f"/api/v1/portfolio/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_public_portfolio_shows_passed_projects_and_certificates(
    client, admin_client, seeded_project, seeded_course_with_lessons
):
    user_id = await _register_and_login(client)
    await client.patch("/api/v1/portfolio/settings", json={"portfolio_public": True})

    submit_resp = await client.post(
        f"/api/v1/projects/{seeded_project}/submissions", json={"submission_url": "https://github.com/x/y"}
    )
    submission_id = submit_resp.json()["id"]

    await client.post(f"/api/v1/lessons/portfolio-test-lesson/complete")
    cert_resp = await client.post(f"/api/v1/courses/{seeded_course_with_lessons}/certificate")
    assert cert_resp.status_code == 201

    # Re-login as admin to review the submission — admin_client and client
    # share one cookie jar, so this switches the active session back.
    await client.post(
        "/api/v1/auth/login", json={"email": "portfolio-admin@test.dev", "password": "correcthorsebattery"}
    )
    review_resp = await admin_client.patch(
        f"/api/v1/admin/project-submissions/{submission_id}", json={"status": "passed"}
    )
    assert review_resp.status_code == 200

    # A fresh, unauthenticated lookup of the learner's public portfolio.
    portfolio_resp = await client.get(f"/api/v1/portfolio/{user_id}")
    assert portfolio_resp.status_code == 200
    body = portfolio_resp.json()
    assert body["display_name"] == "Learner"
    assert len(body["projects"]) == 1
    assert body["projects"][0]["project_title"] == "Portfolio Test Project"
    assert body["projects"][0]["submission_url"] == "https://github.com/x/y"
    assert len(body["certificates"]) == 1
    assert body["certificates"][0]["course_title"] == "Portfolio Test Course"


async def test_unreviewed_submission_does_not_appear_in_portfolio(client, seeded_project):
    user_id = await _register_and_login(client)
    await client.patch("/api/v1/portfolio/settings", json={"portfolio_public": True})
    await client.post(
        f"/api/v1/projects/{seeded_project}/submissions", json={"submission_url": "https://github.com/x/y"}
    )

    resp = await client.get(f"/api/v1/portfolio/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["projects"] == []
