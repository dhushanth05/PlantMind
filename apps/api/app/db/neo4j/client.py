from neo4j import AsyncDriver, AsyncGraphDatabase

from app.core.config import settings


class Neo4jDatabase:
    def __init__(self) -> None:
        self._driver: AsyncDriver | None = None

    @property
    def driver(self) -> AsyncDriver:
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )
        return self._driver

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None


neo4j_database = Neo4jDatabase()
