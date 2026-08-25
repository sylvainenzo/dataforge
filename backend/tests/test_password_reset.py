"""Forgot-password / reset-password flow — didn't exist before this;
the only prior option was an admin running scripts/reset_password.py.
Covers the enumeration-safe generic responses, single-use tokens, and
the graceful 503 when no email provider is configured (the real state
of this deployment until RESEND_API_KEY is set)."""

from urllib.parse import parse_qs, urlparse

import pytest_asyncio


async def _register(client, email="reset-user@test.dev", password="correcthorsebattery"):
    resp = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": password, "display_name": "Reset User"}
    )
    return resp.json()["id"]


def _extract_token(reset_url: str) -> str:
    return parse_qs(urlparse(reset_url).query)["token"][0]


@pytest_asyncio.fixture
async def configured_email(monkeypatch):
    """Fakes email as configured and captures every call instead of
    actually hitting Resend's API."""
    import app.api.v1.auth as auth_module
    from app.core.config import settings

    monkeypatch.setattr(settings, "resend_api_key", "test-key-not-real")
    sent = []

    async def _fake_send(to_email, reset_url, *, expires_in_minutes):
        sent.append({"to": to_email, "url": reset_url})

    monkeypatch.setattr(auth_module, "send_password_reset_email", _fake_send)
    return sent


async def test_forgot_password_503s_when_not_configured(client):
    await _register(client, "unconfigured@test.dev")
    resp = await client.post("/api/v1/auth/forgot-password", json={"email": "unconfigured@test.dev"})
    assert resp.status_code == 503


async def test_forgot_password_generic_message_for_real_email(client, configured_email):
    await _register(client, "real-user@test.dev")
    resp = await client.post("/api/v1/auth/forgot-password", json={"email": "real-user@test.dev"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "If that email is registered, a reset link has been sent."
    assert len(configured_email) == 1
    assert configured_email[0]["to"] == "real-user@test.dev"


async def test_forgot_password_same_generic_message_for_unknown_email(client, configured_email):
    # No registration at all for this address — regression guard for the
    # enumeration side-channel: response must be identical either way, and
    # no email attempt should even be made for an address that isn't real.
    resp = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody-here@test.dev"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "If that email is registered, a reset link has been sent."
    assert configured_email == []


async def test_forgot_password_rate_limited(client):
    for _ in range(3):
        resp = await client.post("/api/v1/auth/forgot-password", json={"email": "ratelimit@test.dev"})
        assert resp.status_code in (200, 503)
    fourth = await client.post("/api/v1/auth/forgot-password", json={"email": "ratelimit@test.dev"})
    assert fourth.status_code == 429


async def test_full_reset_flow_changes_password_and_allows_login(client, configured_email):
    await _register(client, "flow@test.dev", "originalpassword1")

    forgot_resp = await client.post("/api/v1/auth/forgot-password", json={"email": "flow@test.dev"})
    assert forgot_resp.status_code == 200
    token = _extract_token(configured_email[0]["url"])

    reset_resp = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "brandnewpassword2"}
    )
    assert reset_resp.status_code == 200

    old_login = await client.post(
        "/api/v1/auth/login", json={"email": "flow@test.dev", "password": "originalpassword1"}
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/api/v1/auth/login", json={"email": "flow@test.dev", "password": "brandnewpassword2"}
    )
    assert new_login.status_code == 200


async def test_reset_token_is_single_use(client, configured_email):
    await _register(client, "singleuse@test.dev", "originalpassword1")
    await client.post("/api/v1/auth/forgot-password", json={"email": "singleuse@test.dev"})
    token = _extract_token(configured_email[0]["url"])

    first = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "firstnewpassword"}
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "secondnewpassword"}
    )
    assert second.status_code == 400
    assert "already been used" in second.json()["detail"]


async def test_reset_password_rejects_garbage_token(client):
    resp = await client.post(
        "/api/v1/auth/reset-password", json={"token": "not-a-real-token", "new_password": "whatever123"}
    )
    assert resp.status_code == 400
    assert "invalid or has expired" in resp.json()["detail"]


async def test_reset_password_rejects_an_access_token(client, configured_email):
    """Regression guard: a valid but wrong-type token (e.g. someone's own
    access token) must not be accepted as a reset token."""
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongtype@test.dev", "password": "correcthorsebattery", "display_name": "X"},
    )
    assert register_resp.status_code == 201
    access_token = client.cookies.get("access_token")

    resp = await client.post(
        "/api/v1/auth/reset-password", json={"token": access_token, "new_password": "whatever123"}
    )
    assert resp.status_code == 400
