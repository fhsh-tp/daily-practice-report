"""Setup state helpers called from lifespan."""
from __future__ import annotations

from typing import Any

from shared.redis import SETUP_FLAG_KEY


async def init_redis_state(state: Any, redis_client: Any) -> None:
    """Store the Redis client in app.state.redis."""
    state.redis = redis_client


async def check_setup_state(state: Any) -> None:
    """
    Read Redis flag and MongoDB to determine setup state.

    Sets state.system_config to the loaded SystemConfig if configured,
    or None if setup has not been completed.
    Also restores the Redis flag if it is missing but MongoDB has a config.
    """
    from core.system.models import SystemConfig

    redis = state.redis
    flag = await redis.get(SETUP_FLAG_KEY)

    if flag == b"true":
        config = await SystemConfig.find_one()
        state.system_config = config
        return

    # Redis flag absent — check MongoDB as fallback
    config = await SystemConfig.find_one()
    if config is not None:
        # Restore missing Redis flag
        await redis.set(SETUP_FLAG_KEY, "true")
        state.system_config = config
    else:
        state.system_config = None
