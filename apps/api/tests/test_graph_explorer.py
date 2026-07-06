import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.graph import get_graph_explorer_service
from app.main import app
from app.services.graph_explorer_service import GraphExplorerService


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[str, dict | list] = {}

    async def get_json(self, key: str):
        return self.values.get(key)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        self.values[key] = value


class FakeGraphRepository:
    def __init__(self) -> None:
        self.overview_calls = 0

    async def get_overview(self):
        self.overview_calls += 1
        return {
            "total_nodes": 3,
            "total_relationships": 2,
            "node_types": [{"type": "Equipment", "count": 1}, {"type": "Document", "count": 1}],
            "relationship_types": [{"type": "MENTIONED_IN", "count": 1}],
        }

    async def search_nodes(self, query: str, limit: int, offset: int):
        return {
            "nodes": [
                {
                    "id": "neo4j-1",
                    "labels": ["Equipment"],
                    "equipment_id": "P204",
                    "name": "Pump P204",
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset,
        }

    async def get_subgraph(self, node_id: str, depth: int, limit: int):
        return {
            "center_node": {"id": "neo4j-1", "labels": ["Equipment"], "equipment_id": node_id},
            "nodes": [
                {"id": "neo4j-1", "labels": ["Equipment"], "equipment_id": node_id},
                {"id": "neo4j-2", "labels": ["Document"], "document_id": "doc-1"},
            ],
            "relationships": [
                {
                    "id": "rel-1",
                    "type": "MENTIONED_IN",
                    "source": "neo4j-1",
                    "target": "neo4j-2",
                    "document_id": "doc-1",
                }
            ],
        }

    async def get_asset_context(self, equipment_id: str, limit: int, offset: int):
        return {
            "equipment": {"id": "neo4j-1", "labels": ["Equipment"], "equipment_id": equipment_id},
            "connected_incidents": [{"id": "neo4j-2", "labels": ["Incident"], "incident_id": "inc-1"}],
            "connected_documents": [{"id": "neo4j-3", "labels": ["Document"], "document_id": "doc-1"}],
            "connected_personnel": [{"id": "neo4j-4", "labels": ["Person"], "person_id": "person-1"}],
            "failure_modes": [{"id": "neo4j-5", "labels": ["FailureMode"], "name": "Seal failure"}],
            "related_procedures": [{"id": "neo4j-6", "labels": ["Procedure"], "procedure_id": "SOP-17"}],
            "relationships": [
                {"id": "rel-1", "type": "CAUSED_BY", "source": "neo4j-2", "target": "neo4j-1"}
            ],
        }

    async def most_connected_assets(self, limit: int):
        return [{"equipment_id": "P204", "name": "Pump P204", "degree": 7}]

    async def critical_equipment(self, limit: int):
        return [
            {
                "equipment_id": "P204",
                "name": "Pump P204",
                "incident_count": 2,
                "failure_mode_count": 1,
                "degree": 7,
                "criticality_score": 20,
            }
        ]

    async def frequent_failure_modes(self, limit: int):
        return [{"failure_mode": "Seal failure", "mentions": 4}]


@pytest.mark.asyncio
async def test_graph_service_overview_uses_cache() -> None:
    repository = FakeGraphRepository()
    service = GraphExplorerService(repository=repository, cache=FakeCache(), cache_ttl_seconds=30)

    first = await service.get_overview()
    second = await service.get_overview()

    assert first.total_nodes == 3
    assert second.total_relationships == 2
    assert repository.overview_calls == 1


@pytest.mark.asyncio
async def test_graph_service_search_normalizes_nodes() -> None:
    service = GraphExplorerService(repository=FakeGraphRepository(), cache=FakeCache(), cache_ttl_seconds=30)

    result = await service.search_nodes(query="P204", limit=10, offset=0)

    assert result.total == 1
    assert result.nodes[0].id == "neo4j-1"
    assert result.nodes[0].properties["equipment_id"] == "P204"


@pytest.mark.asyncio
async def test_graph_service_asset_context() -> None:
    service = GraphExplorerService(repository=FakeGraphRepository(), cache=FakeCache(), cache_ttl_seconds=30)

    result = await service.get_asset_context(equipment_id="P204", limit=25, offset=0)

    assert result.equipment.properties["equipment_id"] == "P204"
    assert result.connected_incidents[0].labels == ["Incident"]
    assert result.failure_modes[0].properties["name"] == "Seal failure"


def test_graph_routes_are_registered() -> None:
    service = GraphExplorerService(repository=FakeGraphRepository(), cache=FakeCache(), cache_ttl_seconds=30)
    app.dependency_overrides[get_graph_explorer_service] = lambda: service
    try:
        client = TestClient(app)

        response = client.get("/api/v1/graph/overview")

        assert response.status_code == 200
        assert response.json()["total_nodes"] == 3
    finally:
        app.dependency_overrides.clear()
