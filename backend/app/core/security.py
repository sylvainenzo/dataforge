import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class InvalidTokenError(Exception):
    pass


def _create_token(user_id: uuid.UUID, token_type: TokenType, expires_delta: timedelta) -> tuple[str, str]:
    """Returns (encoded_jwt, jti). jti lets refresh tokens be individually
    revoked via the Redis denylist in app/core/token_store.py — a JWT alone
    can't be revoked before it expires."""

    now = datetime.now(UTC)
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(user_id),
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti


def create_access_token(user_id: uuid.UUID) -> str:
    token, _ = _create_token(user_id, TokenType.ACCESS, timedelta(minutes=settings.access_token_expire_minutes))
    return token


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, str, datetime]:
    """Returns (token, jti, expires_at) — the caller needs jti/expires_at to
    manage the Redis denylist on rotation/logout."""

    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    token, jti = _create_token(user_id, TokenType.REFRESH, expires_delta)
    return token, jti, datetime.now(UTC) + expires_delta


def decode_token(token: str, expected_type: TokenType) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type.value:
        raise InvalidTokenError(f"expected a {expected_type.value} token")
    return payload
