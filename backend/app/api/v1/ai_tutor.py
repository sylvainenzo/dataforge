import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.core.security import InvalidTokenError, TokenType, decode_token
from app.core.token_store import check_rate_limit
from app.schemas.ai_tutor import CreateSessionRequest, MessageRead, SessionRead
from app.services import ai_tutor_service
from app.services.ai_tutor_service import AITutorNotConfiguredError
from app.services.auth_service import get_user_by_id

router = APIRouter(prefix="/ai-tutor", tags=["ai-tutor"])


@router.post("/sessions", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    context = {
        k: v
        for k, v in {
            "lesson_title": body.lesson_title,
            "code": body.code,
            "error_message": body.error_message,
            "skill_level": body.skill_level,
        }.items()
        if v is not None
    }
    session = await ai_tutor_service.create_session(db, user_id=current_user.id, mode=body.mode, context=context)
    return session


@router.get("/sessions/{session_id}/messages", response_model=list[MessageRead])
async def get_messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    session = await ai_tutor_service.get_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return await ai_tutor_service.get_message_history(db, session_id)


@router.websocket("/ws/{session_id}")
async def tutor_socket(
    websocket: WebSocket,
    session_id: uuid.UUID,
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if access_token is None:
        await websocket.close(code=4401)
        return
    try:
        payload = decode_token(access_token, TokenType.ACCESS)
    except InvalidTokenError:
        await websocket.close(code=4401)
        return

    user_id = uuid.UUID(payload["sub"])
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        await websocket.close(code=4401)
        return

    session = await ai_tutor_service.get_session(db, session_id, user_id)
    if session is None:
        await websocket.close(code=4404)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")

            if not await check_rate_limit("ai-tutor", str(user_id), 15):
                await websocket.send_json({"type": "error", "data": "Rate limit exceeded — slow down."})
                continue

            try:
                async for chunk in ai_tutor_service.stream_reply(db, session=session, user_message=user_message):
                    await websocket.send_json({"type": "token", "data": chunk})
                await websocket.send_json({"type": "done"})
            except AITutorNotConfiguredError:
                await websocket.send_json(
                    {"type": "error", "data": "The AI Tutor is not configured on this server (no API key set)."}
                )
    except WebSocketDisconnect:
        pass
