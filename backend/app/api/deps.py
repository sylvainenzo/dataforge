import uuid
from dataclasses import dataclass

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import InvalidTokenError, TokenType, decode_token
from app.core.token_store import is_refresh_token_revoked
from app.services.auth_service import get_display_name, get_user_by_id, get_user_roles

_CREDENTIALS_ERROR = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


@dataclass
class CurrentUser:
    id: uuid.UUID
    email: str
    display_name: str | None
    roles: list[str]


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    if access_token is None:
        raise _CREDENTIALS_ERROR
    try:
        payload = decode_token(access_token, TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise _CREDENTIALS_ERROR from exc

    user_id = uuid.UUID(payload["sub"])
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_ERROR

    roles = await get_user_roles(db, user_id)
    display_name = await get_display_name(db, user_id)
    return CurrentUser(id=user.id, email=user.email, display_name=display_name, roles=roles)


def require_role(*allowed_roles: str):
    async def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not set(current_user.roles) & set(allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return _check


async def get_refresh_payload(refresh_token: str | None = Cookie(default=None)) -> dict:
    if refresh_token is None:
        raise _CREDENTIALS_ERROR
    try:
        payload = decode_token(refresh_token, TokenType.REFRESH)
    except InvalidTokenError as exc:
        raise _CREDENTIALS_ERROR from exc

    if await is_refresh_token_revoked(payload["jti"]):
        raise _CREDENTIALS_ERROR
    return payload
