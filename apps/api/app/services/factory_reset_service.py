import asyncio
import logging
import shutil
from pathlib import Path

from app.core.config import ROOT_DIR, settings
from app.db.mongodb.client import mongo_database
from app.db.neo4j.client import neo4j_database
from app.db.redis.cache import RedisCache
from app.domain.admin.schemas import FactoryResetDeletedCounts, FactoryResetResponse

logger = logging.getLogger(__name__)


RUNTIME_MONGO_COLLECTIONS = (
    "documents",
    "chunks",
    "embeddings",
    "document_entities",
    "incidents",
    "asset_events",
    "asset_intelligence",
    "analytics",
    "risk_outputs",
    "compliance_evidence",
    "alerts",
)

CACHE_PATTERNS = (
    "search:*",
    "chat:*",
    "conversation:*",
    "dashboard:*",
    "graph:*",
    "embedding:*",
    "embeddings:*",
    "digital_twin:*",
)

TEMP_DIRECTORY_NAMES = ("tmp", "temp", "processing", "uploads", "artifacts")


class FactoryResetService:
    def __init__(self, cache: RedisCache | None = None) -> None:
        self.db = mongo_database.database
        self.cache = cache or RedisCache()

    async def reset(self) -> FactoryResetResponse:
        mongo_counts, graph_counts, cache_keys, uploaded_files = await asyncio.gather(
            self._clear_mongodb(),
            self._clear_neo4j(),
            self._clear_redis(),
            self._clear_runtime_files(),
        )

        deleted = FactoryResetDeletedCounts(
            documents=mongo_counts.get("documents", 0),
            chunks=mongo_counts.get("chunks", 0),
            embeddings=mongo_counts.get("embeddings", 0),
            graphNodes=graph_counts["nodes"],
            graphRelationships=graph_counts["relationships"],
            cacheKeys=cache_keys,
            uploadedFiles=uploaded_files,
        )
        logger.info("factory_reset_complete", extra={"deleted": deleted.model_dump(by_alias=True)})
        return FactoryResetResponse(deleted=deleted)

    async def _clear_mongodb(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for collection_name in RUNTIME_MONGO_COLLECTIONS:
            collection = self.db[collection_name]
            count = await collection.count_documents({})
            result = await collection.delete_many({})
            counts[collection_name] = int(result.deleted_count or count)
        return counts

    async def _clear_neo4j(self) -> dict[str, int]:
        query = """
        MATCH ()-[r]->()
        WITH count(r) AS relationship_count
        MATCH (n)
        WITH relationship_count, count(n) AS node_count
        MATCH (n)
        DETACH DELETE n
        RETURN relationship_count, node_count
        """
        async with neo4j_database.driver.session(database=settings.neo4j_database) as session:
            record = await (await session.run(query)).single()
        return {
            "nodes": int(record["node_count"]) if record else 0,
            "relationships": int(record["relationship_count"]) if record else 0,
        }

    async def _clear_redis(self) -> int:
        deleted = 0
        for pattern in CACHE_PATTERNS:
            deleted += await self.cache.delete_pattern(pattern)
        return deleted

    async def _clear_runtime_files(self) -> int:
        storage_root = Path(settings.document_storage_root).resolve()
        self._ensure_runtime_path(storage_root)
        deleted = await asyncio.to_thread(self._clear_directory_contents, storage_root)
        await asyncio.to_thread(storage_root.mkdir, parents=True, exist_ok=True)

        for directory_name in TEMP_DIRECTORY_NAMES:
            temp_dir = storage_root / directory_name
            await asyncio.to_thread(temp_dir.mkdir, parents=True, exist_ok=True)
        return deleted

    @staticmethod
    def _ensure_runtime_path(path: Path) -> None:
        protected_names = {".git", ".github", "apps", "infra", "scripts", "docs"}
        if path == ROOT_DIR or ROOT_DIR in path.parents:
            raise RuntimeError(f"Refusing to factory reset inside the source tree: {path}")
        if any(part in protected_names for part in path.parts):
            raise RuntimeError(f"Refusing to factory reset protected path: {path}")

    @classmethod
    def _clear_directory_contents(cls, directory: Path) -> int:
        if not directory.exists():
            return 0

        deleted = 0
        for child in directory.iterdir():
            if child.name in {".git", ".github", ".env"}:
                continue
            if child.is_dir() and child.name in TEMP_DIRECTORY_NAMES:
                deleted += cls._clear_directory_contents(child)
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink(missing_ok=True)
            deleted += 1
        return deleted
