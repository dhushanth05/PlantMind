import hashlib
from datetime import date, datetime
from typing import Any

from app.db.neo4j.graph_repository import GraphRepository
from app.db.redis.cache import RedisCache
from app.core.config import settings
from app.domain.graph.schemas import (
    AssetContext,
    ConnectedAssetMetric,
    CriticalEquipmentMetric,
    FailureModeMetric,
    GraphAnalytics,
    GraphNode,
    GraphOverview,
    GraphRelationship,
    GraphSearchResult,
    GraphSubgraph,
    GraphTypeCount,
)


class GraphExplorerService:
    def __init__(
        self,
        repository: GraphRepository | None = None,
        cache: RedisCache | None = None,
        cache_ttl_seconds: int | None = None,
    ) -> None:
        self.repository = repository or GraphRepository()
        self.cache = cache or RedisCache()
        self.cache_ttl_seconds = cache_ttl_seconds or settings.graph_cache_ttl_seconds

    async def get_overview(self) -> GraphOverview:
        cache_key = "graph:overview"
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return GraphOverview.model_validate(cached)

        data = await self.repository.get_overview()
        overview = GraphOverview(
            total_nodes=data["total_nodes"],
            total_relationships=data["total_relationships"],
            node_types=[GraphTypeCount.model_validate(item) for item in data["node_types"]],
            relationship_types=[GraphTypeCount.model_validate(item) for item in data["relationship_types"]],
        )
        await self.cache.set_json(cache_key, overview.model_dump(mode="json"), self.cache_ttl_seconds)
        return overview

    async def search_nodes(self, query: str, limit: int, offset: int) -> GraphSearchResult:
        cache_key = self._cache_key("graph:search", query, limit, offset)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return GraphSearchResult.model_validate(cached)

        data = await self.repository.search_nodes(query=query, limit=limit, offset=offset)
        result = GraphSearchResult(
            nodes=[self._normalize_node(node) for node in data["nodes"]],
            total=data["total"],
            limit=data["limit"],
            offset=data["offset"],
        )
        await self.cache.set_json(cache_key, result.model_dump(mode="json"), self.cache_ttl_seconds)
        return result

    async def get_subgraph(self, node_id: str, depth: int, limit: int) -> GraphSubgraph:
        cache_key = self._cache_key("graph:subgraph", node_id, depth, limit)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return GraphSubgraph.model_validate(cached)

        data = await self.repository.get_subgraph(node_id=node_id, depth=depth, limit=limit)
        if data.get("center_node") is None:
            raise LookupError(f"Graph node not found: {node_id}")

        result = GraphSubgraph(
            center_node=self._normalize_node(data["center_node"]),
            nodes=[self._normalize_node(node) for node in data["nodes"]],
            relationships=[self._normalize_relationship(relationship) for relationship in data["relationships"]],
        )
        await self.cache.set_json(cache_key, result.model_dump(mode="json"), self.cache_ttl_seconds)
        return result

    async def get_asset_context(self, equipment_id: str, limit: int, offset: int) -> AssetContext:
        cache_key = self._cache_key("graph:asset", equipment_id, limit, offset)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return AssetContext.model_validate(cached)

        data = await self.repository.get_asset_context(equipment_id=equipment_id, limit=limit, offset=offset)
        if data is None:
            raise LookupError(f"Equipment not found: {equipment_id}")

        result = AssetContext(
            equipment=self._normalize_node(data["equipment"]),
            connected_incidents=[self._normalize_node(node) for node in data["connected_incidents"]],
            connected_documents=[self._normalize_node(node) for node in data["connected_documents"]],
            connected_personnel=[self._normalize_node(node) for node in data["connected_personnel"]],
            failure_modes=[self._normalize_node(node) for node in data["failure_modes"]],
            related_procedures=[self._normalize_node(node) for node in data["related_procedures"]],
            relationships=[self._normalize_relationship(relationship) for relationship in data["relationships"]],
        )
        await self.cache.set_json(cache_key, result.model_dump(mode="json"), self.cache_ttl_seconds)
        return result

    async def get_analytics(self, limit: int) -> GraphAnalytics:
        cache_key = self._cache_key("graph:analytics", limit)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return GraphAnalytics.model_validate(cached)

        most_connected, critical, failure_modes = await self._load_analytics(limit)
        analytics = GraphAnalytics(
            most_connected_assets=[ConnectedAssetMetric.model_validate(item) for item in most_connected],
            critical_equipment=[CriticalEquipmentMetric.model_validate(item) for item in critical],
            frequent_failure_modes=[FailureModeMetric.model_validate(item) for item in failure_modes],
        )
        await self.cache.set_json(cache_key, analytics.model_dump(mode="json"), self.cache_ttl_seconds)
        return analytics

    async def _load_analytics(self, limit: int) -> tuple[list[dict], list[dict], list[dict]]:
        most_connected = await self.repository.most_connected_assets(limit=limit)
        critical = await self.repository.critical_equipment(limit=limit)
        failure_modes = await self.repository.frequent_failure_modes(limit=limit)
        return most_connected, critical, failure_modes

    @staticmethod
    def _normalize_node(raw: dict) -> GraphNode:
        properties = {key: _json_safe(value) for key, value in raw.items() if key not in {"id", "labels"}}
        return GraphNode(id=str(raw["id"]), labels=list(raw.get("labels", [])), properties=properties)

    @staticmethod
    def _normalize_relationship(raw: dict) -> GraphRelationship:
        properties = {
            key: _json_safe(value) for key, value in raw.items() if key not in {"id", "type", "source", "target"}
        }
        return GraphRelationship(
            id=str(raw["id"]),
            type=str(raw["type"]),
            source=str(raw["source"]),
            target=str(raw["target"]),
            properties=properties,
        )

    @staticmethod
    def _cache_key(prefix: str, *parts: object) -> str:
        joined = "|".join(str(part) for part in parts)
        digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime | date):
        return value.isoformat()
    if hasattr(value, "iso_format"):
        return value.iso_format()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value
