"""Certificates — the model existed with zero rows and zero logic before
this. Covers completion-gated issuing, idempotent re-issuing, PDF
download, and public verification (app/services/certificate_service.py,
app/api/v1/certificates.py).

Also a regression guard for a real bug found while building this: several
models used `server_default="now()"` (a bare Python string), which Alembic
autogenerate baked into the DB schema as a *frozen literal timestamp*
rather than a dynamic now() call — every row relying on that server
default got the exact same fake timestamp forever. Fixed in migration
a119e0f1bd4b for 11 columns across 11 tables; the test below asserts a
freshly issued certificate's issued_at is actually close to "now", not a
suspiciously old fixed value.
"""

from datetime import UTC, datetime

import pytest_asyncio


@pytest_asyncio.fixture
async def seeded_course_with_lessons():
    from app.core.db import AsyncSessionLocal
    from app.models.base import LearningLevel
    from app.models.curriculum import Course, Lesson, Module

    async with AsyncSessionLocal() as db:
        course = Course(
            title="Certificate Test Course", slug="certificate-test-course", level=LearningLevel.BEGINNER, published=True
        )
        db.add(course)
        await db.flush()
        module = Module(course_id=course.id, title="Module", slug="certificate-test-module", order=1)
        db.add(module)
        await db.flush()

        slugs = ["cert-lesson-a", "cert-lesson-b"]
        for i, slug in enumerate(slugs):
            db.add(
                Lesson(
                    module_id=module.id, title=f"Lesson {i}", slug=slug, order=i + 1,
                    content={"blocks": []}, published=True,
                )
            )
        await db.commit()
        return {"course_slug": course.slug, "lesson_slugs": slugs}


async def _register_and_login(client, email="cert-learner@test.dev"):
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "correcthorsebattery", "display_name": "Learner"}
    )


async def test_cannot_issue_certificate_for_incomplete_course(client, seeded_course_with_lessons):
    await _register_and_login(client)
    resp = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    assert resp.status_code == 400


async def test_issue_certificate_after_completing_all_lessons(client, seeded_course_with_lessons):
    await _register_and_login(client)
    for slug in seeded_course_with_lessons["lesson_slugs"]:
        complete_resp = await client.post(f"/api/v1/lessons/{slug}/complete")
        assert complete_resp.status_code == 204

    before = datetime.now(UTC)
    resp = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    assert resp.status_code == 201
    body = resp.json()
    assert body["certificate_number"].startswith("DF-")

    # Regression guard for the frozen-timestamp bug: issued_at must be
    # genuinely close to now, not some old fixed value.
    issued_at = datetime.fromisoformat(body["issued_at"])
    assert (issued_at - before).total_seconds() < 10

    list_resp = await client.get("/api/v1/certificates")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


async def test_issuing_twice_returns_the_same_certificate(client, seeded_course_with_lessons):
    await _register_and_login(client)
    for slug in seeded_course_with_lessons["lesson_slugs"]:
        await client.post(f"/api/v1/lessons/{slug}/complete")

    first = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    second = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    assert first.json()["certificate_number"] == second.json()["certificate_number"]

    list_resp = await client.get("/api/v1/certificates")
    assert len(list_resp.json()) == 1  # not duplicated


async def test_download_certificate_returns_a_real_pdf(client, seeded_course_with_lessons):
    await _register_and_login(client)
    for slug in seeded_course_with_lessons["lesson_slugs"]:
        await client.post(f"/api/v1/lessons/{slug}/complete")

    issue_resp = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    certificate_id = issue_resp.json()["id"]

    download_resp = await client.get(f"/api/v1/certificates/{certificate_id}/download")
    assert download_resp.status_code == 200
    assert download_resp.headers["content-type"] == "application/pdf"
    assert download_resp.content.startswith(b"%PDF")


async def test_public_verification_works_without_auth(client, seeded_course_with_lessons):
    await _register_and_login(client)
    for slug in seeded_course_with_lessons["lesson_slugs"]:
        await client.post(f"/api/v1/lessons/{slug}/complete")
    issue_resp = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    certificate_number = issue_resp.json()["certificate_number"]

    # A fresh, unauthenticated client-equivalent call: no login here.
    verify_resp = await client.get(f"/api/v1/certificates/verify/{certificate_number}")
    assert verify_resp.status_code == 200
    body = verify_resp.json()
    assert body["course_title"] == "Certificate Test Course"


async def test_verification_404s_for_unknown_number(client):
    resp = await client.get("/api/v1/certificates/verify/DF-DOESNOTEXIST")
    assert resp.status_code == 404


async def test_certificate_endpoints_require_auth(client, seeded_course_with_lessons):
    resp = await client.post(f"/api/v1/courses/{seeded_course_with_lessons['course_slug']}/certificate")
    assert resp.status_code == 401

    list_resp = await client.get("/api/v1/certificates")
    assert list_resp.status_code == 401
