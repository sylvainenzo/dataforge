import pytest


async def test_register_creates_user_with_student_role(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "student@test.dev", "password": "correcthorsebattery", "display_name": "Test Student"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "student@test.dev"
    assert body["roles"] == ["student"]
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


async def test_duplicate_email_is_rejected(client):
    payload = {"email": "dup@test.dev", "password": "correcthorsebattery", "display_name": "Dup"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400


async def test_login_with_wrong_password_is_rejected(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@test.dev", "password": "correcthorsebattery", "display_name": "X"},
    )
    resp = await client.post("/api/v1/auth/login", json={"email": "wrongpw@test.dev", "password": "nope"})
    assert resp.status_code == 401


async def test_me_requires_authentication(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user_after_login(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@test.dev", "password": "correcthorsebattery", "display_name": "Me"},
    )
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.dev"


async def test_logout_then_me_is_unauthenticated(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@test.dev", "password": "correcthorsebattery", "display_name": "X"},
    )
    logout_resp = await client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200

    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_refresh_rotates_token(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@test.dev", "password": "correcthorsebattery", "display_name": "X"},
    )
    old_refresh = client.cookies.get("refresh_token")

    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 200
    new_refresh = client.cookies.get("refresh_token")
    assert new_refresh != old_refresh


@pytest.mark.parametrize("password", ["short"])
async def test_registration_rejects_short_password(client, password):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "shortpw@test.dev", "password": password, "display_name": "X"},
    )
    assert resp.status_code == 422
