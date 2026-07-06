import json
import logging

from app.db.redis.client import redis_database
from app.domain.chat.schemas import ConversationTurn

logger = logging.getLogger(__name__)


class ConversationMemory:
    def __init__(self, max_turns: int = 8, ttl_seconds: int = 86_400) -> None:
        self.max_turns = max_turns
        self.ttl_seconds = ttl_seconds

    async def load(self, session_id: str) -> list[ConversationTurn]:
        key = self._key(session_id)
        try:
            values = await redis_database.client.lrange(key, 0, self.max_turns * 2 - 1)
        except Exception:
            logger.exception("conversation_memory_load_failed", extra={"session_id": session_id})
            return []
        turns = [ConversationTurn.model_validate(json.loads(value)) for value in values]
        return list(reversed(turns))

    async def append(self, session_id: str, *turns: ConversationTurn) -> None:
        if not turns:
            return
        key = self._key(session_id)
        payloads = [turn.model_dump_json() for turn in turns]
        try:
            await redis_database.client.lpush(key, *payloads)
            await redis_database.client.ltrim(key, 0, self.max_turns * 2 - 1)
            await redis_database.client.expire(key, self.ttl_seconds)
        except Exception:
            logger.exception("conversation_memory_append_failed", extra={"session_id": session_id})

    @staticmethod
    def _key(session_id: str) -> str:
        return f"chat:session:{session_id}:turns"

