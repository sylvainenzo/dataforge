import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def check_execution_rate_limit(user_id: str) -> bool:
    key = f"ratelimit:execution:{user_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    return count <= settings.execution_rate_limit_per_minute
