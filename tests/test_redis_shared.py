"""Tests for shared Redis client factory."""
import pytest


async def test_get_redis_client_returns_client():
    """get_redis_client returns a Redis client instance."""
    from shared.redis import get_redis_client
    client = get_redis_client()
    assert client is not None


async def test_system_configured_key_operations():
    """Redis caches system configuration state using system:configured key."""
    import fakeredis.aioredis as fakeredis
    from shared.redis import SETUP_FLAG_KEY

    r = fakeredis.FakeRedis()
    assert SETUP_FLAG_KEY == "system:configured"
    await r.set(SETUP_FLAG_KEY, "true")
    val = await r.get(SETUP_FLAG_KEY)
    assert val == b"true"
    await r.aclose()
