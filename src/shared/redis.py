"""Shared Redis client factory."""
import os
import redis.asyncio as aioredis

SETUP_FLAG_KEY = "system:configured"


def get_redis_client() -> aioredis.Redis:
    """Return an async Redis client from REDIS_URL env var."""
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return aioredis.from_url(url, decode_responses=False)
