from datetime import UTC, datetime

from app.core.redis import redis_client

_REVOKED_PREFIX = "revoked_jti:"
_RATE_LIMIT_PREFIX = "ratelimit:"


async def revoke_jti(jti: str, expires_at: datetime) -> None:
    """Adds any JWT's jti to a Redis denylist until it would have expired
    anyway, so Redis self-cleans. Used for refresh-token rotation/logout
    (Phase 1 §13) and for single-use tokens like password resets, where
    "revoked" just means "already used"."""

    ttl_seconds = max(1, int((expires_at - datetime.now(UTC)).total_seconds()))
    await redis_client.set(f"{_REVOKED_PREFIX}{jti}", "1", ex=ttl_seconds)


async def is_jti_revoked(jti: str) -> bool:
    return await redis_client.exists(f"{_REVOKED_PREFIX}{jti}") == 1


async def check_rate_limit(scope: str, identifier: str, limit_per_minute: int) -> bool:
    """Fixed 60s-window counter. Returns True if the request is allowed,
    False if the caller has exceeded limit_per_minute. Applied to
    login/register per Phase 1 §13's 'rate limiting on auth endpoints'."""

    key = f"{_RATE_LIMIT_PREFIX}{scope}:{identifier}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    return count <= limit_per_minute
