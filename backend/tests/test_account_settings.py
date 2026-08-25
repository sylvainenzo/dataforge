"""Self-service account settings — updating display name and changing
password — had no endpoints at all before this."""


async def _register(client, email="settings-user@test.dev", password="correcthorsebattery"):
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": password, "display_name": "Original Name"}
    )


async def test_update_display_name(client):
    await _register(client)
    resp = await client.patch("/api/v1/auth/me", json={"display_name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "New Name"

    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.json()["display_name"] == "New Name"


async def test_update_display_name_requires_auth(client):
    resp = await client.patch("/api/v1/auth/me", json={"display_name": "New Name"})
    assert resp.status_code == 401


async def test_change_password_with_wrong_current_password_fails(client):
    await _register(client)
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
    )
    assert resp.status_code == 400


async def test_change_password_succeeds_and_old_password_stops_working(client):
    email = "settings-user2@test.dev"
    await _register(client, email=email, password="correcthorsebattery")

    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "correcthorsebattery", "new_password": "newpassword123"},
    )
    assert resp.status_code == 200

    old_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "correcthorsebattery"})
    assert old_login.status_code == 401

    new_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "newpassword123"})
    assert new_login.status_code == 200


async def test_change_password_requires_auth(client):
    resp = await client.post(
        "/api/v1/auth/change-password", json={"current_password": "a", "new_password": "newpassword123"}
    )
    assert resp.status_code == 401


async def test_change_password_rejects_short_new_password(client):
    await _register(client)
    resp = await client.post(
        "/api/v1/auth/change-password", json={"current_password": "correcthorsebattery", "new_password": "short"}
    )
    assert resp.status_code == 422
