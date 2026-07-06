import json
import logging
from typing import Any

from app.db.redis.client import redis_database

logger = logging.getLogger(__name__)


class RedisCache:
    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        try:
            raw = await redis_database.client.get(key)
        except Exception:
            logger.exception("redis_cache_get_failed", extra={"key": key})
            return None
        if raw is None:
            return None
        return json.loads(raw)

    async def set_json(self, key: str, value: dict[str, Any] | list[Any], ttl_seconds: int) -> None:
        try:
            await redis_database.client.setex(key, ttl_seconds, json.dumps(value))
        except Exception:
            logger.exception("redis_cache_set_failed", extra={"key": key})

    async def delete_pattern(self, pattern: str) -> int:
        deleted = 0
        try:
            async for key in redis_database.client.scan_iter(match=pattern):
                deleted += await redis_database.client.delete(key)
        except Exception:
            logger.exception("redis_cache_delete_pattern_failed", extra={"pattern": pattern})
        return deleted
