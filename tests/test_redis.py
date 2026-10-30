import asyncio
import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from app.core.config import settings
from app.core.errors import DomainError
from app.core.redis import rate_limit


@pytest.mark.integration
async def test_atomic_rate_limit_across_concurrent_requests(monkeypatch):
    url = os.getenv("TEST_REDIS_URL")
    if not url:
        pytest.skip("Set TEST_REDIS_URL to a disposable Redis database.")
    redis = Redis.from_url(url, decode_responses=True)
    monkeypatch.setattr(settings, "request_limit_per_minute", 3)
    subject = "synthetic-" + uuid4().hex
    try:
        values = await asyncio.gather(
            *(rate_limit(redis, subject) for _ in range(10)), return_exceptions=True
        )
        assert sum(v is None for v in values) == 3
        denied = [v for v in values if isinstance(v, DomainError)]
        assert len(denied) == 7 and all(v.status == 429 for v in denied)
    finally:
        await redis.aclose()
