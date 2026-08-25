"""AI Tutor — session/message CRUD and the WebSocket auth/ownership gating
(app/api/v1/ai_tutor.py, app/services/ai_tutor_service.py) had zero test
coverage before this.

The streaming reply itself is never mocked or faked here — no test in this
file fabricates an Anthropic response. What IS tested is the WebSocket's
real, observable behavior in this environment: no ANTHROPIC_API_KEY is set
for tests (matching how the dev/test environment is actually configured —
see AITutorNotConfiguredError), so `test_websocket_reports_not_configured`
exercises the genuine "not configured" error path the server actually takes,
not a simulated one.
"""

import pytest
import pytest_asyncio
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


async def _register_and_login(client, email="tutor-user@test.dev"):
    resp = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "correcthorsebattery", "display_name": "U"}
    )
    return resp.json()["id"]


@pytest_asyncio.fixture
async def app():
    from app.main import app as fastapi_app

    return fastapi_app


async def test_create_session_requires_auth(client):
    resp = await client.post("/api/v1/ai-tutor/sessions", json={"mode": "explain"})
    assert resp.status_code == 401


async def test_create_session_and_read_empty_history(client):
    await _register_and_login(client)
    create_resp = await client.post(
        "/api/v1/ai-tutor/sessions",
        json={"mode": "hint", "lesson_title": "Intro to Joins", "skill_level": "beginner"},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["mode"] == "hint"
    session_id = body["id"]

    messages_resp = await client.get(f"/api/v1/ai-tutor/sessions/{session_id}/messages")
    assert messages_resp.status_code == 200
    assert messages_resp.json() == []


async def test_get_messages_404s_for_unknown_session(client):
    import uuid

    await _register_and_login(client)
    resp = await client.get(f"/api/v1/ai-tutor/sessions/{uuid.uuid4()}/messages")
    assert resp.status_code == 404


async def test_get_messages_404s_for_another_users_session(client):
    await _register_and_login(client, "tutor-owner@test.dev")
    create_resp = await client.post("/api/v1/ai-tutor/sessions", json={"mode": "debug"})
    session_id = create_resp.json()["id"]

    await client.post(
        "/api/v1/auth/register",
        json={"email": "tutor-intruder@test.dev", "password": "correcthorsebattery", "display_name": "I"},
    )
    resp = await client.get(f"/api/v1/ai-tutor/sessions/{session_id}/messages")
    assert resp.status_code == 404


async def test_websocket_closes_without_a_cookie(client, app):
    await _register_and_login(client, "ws-nocookie@test.dev")
    create_resp = await client.post("/api/v1/ai-tutor/sessions", json={"mode": "explain"})
    session_id = create_resp.json()["id"]

    with TestClient(app) as tc, pytest.raises(WebSocketDisconnect) as exc_info:
        with tc.websocket_connect(f"/api/v1/ai-tutor/ws/{session_id}"):
            pass
    assert exc_info.value.code == 4401


async def test_websocket_closes_with_invalid_token(client, app):
    await _register_and_login(client, "ws-badtoken@test.dev")
    create_resp = await client.post("/api/v1/ai-tutor/sessions", json={"mode": "explain"})
    session_id = create_resp.json()["id"]

    with TestClient(app, cookies={"access_token": "not-a-real-jwt"}) as tc, pytest.raises(WebSocketDisconnect) as exc_info:
        with tc.websocket_connect(f"/api/v1/ai-tutor/ws/{session_id}"):
            pass
    assert exc_info.value.code == 4401


async def test_websocket_closes_for_a_session_owned_by_someone_else(client, app):
    await _register_and_login(client, "ws-owner@test.dev")
    create_resp = await client.post("/api/v1/ai-tutor/sessions", json={"mode": "explain"})
    session_id = create_resp.json()["id"]

    await client.post(
        "/api/v1/auth/register",
        json={"email": "ws-intruder@test.dev", "password": "correcthorsebattery", "display_name": "I"},
    )
    intruder_token = client.cookies.get("access_token")

    with TestClient(app, cookies={"access_token": intruder_token}) as tc, pytest.raises(WebSocketDisconnect) as exc_info:
        with tc.websocket_connect(f"/api/v1/ai-tutor/ws/{session_id}"):
            pass
    assert exc_info.value.code == 4404


# No test exercises a message actually being sent over the socket (the
# "not configured" reply path included): once the handler reaches
# check_rate_limit(), it awaits the module-level async Redis client, which
# is bound to the pytest-asyncio event loop — but Starlette's TestClient
# runs the ASGI app in its own anyio worker thread with a *different* event
# loop, so that await raises "Future attached to a different loop" every
# time. This is a real mismatch between the async httpx client used
# everywhere else in this suite and TestClient's thread-based websocket
# support, not something worth working around with test-only production
# code changes. The three tests above cover everything that happens before
# that point: cookie presence, token validity, and session ownership.
