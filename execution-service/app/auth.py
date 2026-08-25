import uuid

from jose import JWTError, jwt

from app.config import settings


class InvalidTokenError(Exception):
    pass


def verify_access_token(token: str) -> uuid.UUID:
    """Independently verifies the Core API's access-token cookie using the
    shared JWT secret — no network round-trip to the Core API needed per
    request, matching the internal-trust relationship described in
    Phase 1 §3."""

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != "access":
        raise InvalidTokenError("not an access token")
    return uuid.UUID(payload["sub"])
