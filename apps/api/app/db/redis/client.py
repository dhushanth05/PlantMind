import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


class RedisDatabase:
    def __init__(self) -> None:
        self._client: Redis | None = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            self._client = redis.from_url(settings.redis_url, decode_responses=True)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


redis_database = RedisDatabase()

