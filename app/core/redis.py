"""Redis is a rate limiter and Celery broker, never the authority for consent."""

import hashlib

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.errors import DomainError

RATE_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('EXPIRE', KEYS[1], 60) end
return count
"""


def create_redis():
    return Redis.from_url(
        settings.redis_url, socket_timeout=2, socket_connect_timeout=2, decode_responses=True
    )


async def rate_limit(redis, subject):
    key = "medilink:rate:" + hashlib.sha256(subject.encode()).hexdigest()
    try:
        count = await redis.eval(RATE_SCRIPT, 1, key)
    except RedisError as exc:
        raise DomainError(
            503, "REDIS_UNAVAILABLE", "Request protection is temporarily unavailable."
        ) from exc
    if count > settings.request_limit_per_minute:
        raise DomainError(429, "RATE_LIMITED", "Too many requests. Try again shortly.")
