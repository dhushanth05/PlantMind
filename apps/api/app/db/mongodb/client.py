from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoDatabase:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None

    @property
    def client(self) -> AsyncIOMotorClient:
        if self._client is None:
            self._client = AsyncIOMotorClient(settings.mongodb_uri)
        return self._client

    @property
    def database(self) -> AsyncIOMotorDatabase:
        return self.client[settings.mongodb_database]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None


mongo_database = MongoDatabase()
