import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.assets import get_digital_twin_service
from app.domain.assets.schemas import RelatedAsset, TimelineEvent
from app.domain.graph.schemas import AssetContext, GraphNode, GraphRelationship
from app.domain.search.schemas import HybridGraphContext, RetrievalContext
from app.main import app
from app.services.assets.digital_twin_service import DigitalTwinService
from app.services.assets.health_score_service import HealthScoreService
from app.services.assets.risk_service import RiskService


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[str, dict | list] = {}

    async def get_json(self, key: str):
        return self.values.get(key)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        self.values[key] = value


class FakeAssetService:
    def __init__(self) -> None:
        self.calls = 0

    async def get_asset_context(self, asset_id: str) -> AssetContext:
        self.calls += 1
        equipment = GraphNode(id="eq-1", labels=["Equipment"], properties={"equipment_id": asset_id, "name": "Pump P204"})
        incident = GraphNode(id="inc-1", labels=["Incident"], properties={"name": "Seal leakage incident"})
        document = GraphNode(id="doc-1", labels=["Document"], properties={"document_id": "doc-a"})
        engineer = GraphNode(id="person-1", labels=["Person"], properties={"name": "Ravi"})
        failure = GraphNode(id="fm-1", labels=["FailureMode"], properties={"name": "Seal Leakage"})
        procedure = GraphNode(id="proc-1", labels=["Procedure"], properties={"name": "SOP-17"})
        relationship = GraphRelationship(id="rel-1", type="CAUSED_BY", source="inc-1", target="eq-1")
        return AssetContext(
            equipment=equipment,
            connected_incidents=[incident],
            connected_documents=[document],
            connected_personnel=[engineer],
            failure_modes=[failure],
            related_procedures=[procedure],
            relationships=[relationship],
        )

    async def get_maintenance_history(self, asset_id: str) -> list[TimelineEvent]:
        return [
            TimelineEvent(
                event_type="Maintenance",
                title="Seal replacement",
                description="Seal replaced during scheduled maintenance.",
                timestamp="2026-06-01T00:00:00",
                source="MongoDB",
            )
        ]

    async def get_inspection_findings(self, asset_id: str) -> list[dict]:
        return [{"severity": "medium", "description": "Minor vibration finding"}]

    async def get_retrieval_context(self, asset_id: str) -> RetrievalContext:
        context = await self.get_asset_context(asset_id)
        related_asset = GraphNode(id="eq-2", labels=["Equipment"], properties={"equipment_id": "P205", "name": "Pump P205"})
        graph_context = HybridGraphContext(
            asset_contexts=[context],
            related_nodes=[context.equipment, related_asset, *context.connected_incidents, *context.related_procedures],
            relationships=context.relationships,
        )
        return RetrievalContext(
            query="asset context",
            chunks=[],
            graph_context=graph_context,
            asset_context=[context],
            incidents=context.connected_incidents,
            procedures=context.related_procedures,
        )

    def related_assets(self, context: AssetContext, retrieval_nodes: list[GraphNode]):
        return [
            RelatedAsset(
                asset_id="P205",
                name="Pump P205",
                relationship="GraphContext",
                reason="Shared failure context.",
            )
        ]


@pytest.mark.asyncio
async def test_digital_twin_service_builds_and_caches_twin() -> None:
    fake_asset_service = FakeAssetService()
    service = DigitalTwinService(asset_service=fake_asset_service, cache=FakeCache())

    first = await service.get_digital_twin("P204")
    second = await service.get_digital_twin("P204")

    assert first.asset.properties["equipment_id"] == "P204"
    assert first.health_score.score <= 100
    assert first.risk_level.level in {"Low", "Medium", "High", "Critical"}
    assert first.recommendations
    assert first.related_assets[0].asset_id == "P205"
    assert second.asset.properties["equipment_id"] == "P204"
    assert fake_asset_service.calls >= 2


def test_health_and_risk_scoring_reflect_asset_evidence() -> None:
    context = asyncio.run(FakeAssetService().get_asset_context("P204"))
    health = HealthScoreService().compute(
        context=context,
        maintenance_history=[],
        inspection_findings=[{"severity": "high"}],
        graph_degree=12,
    )
    risk = RiskService().assess(context=context, health_score=health, graph_degree=12)

    assert health.score < 88
    assert risk.score > 0


def test_digital_twin_route_returns_asset_context() -> None:
    service = DigitalTwinService(asset_service=FakeAssetService(), cache=FakeCache())
    app.dependency_overrides[get_digital_twin_service] = lambda: service
    try:
        client = TestClient(app)
        response = client.get("/api/v1/assets/P204/digital-twin")

        assert response.status_code == 200
        payload = response.json()
        assert payload["asset"]["properties"]["equipment_id"] == "P204"
        assert payload["graph_summary"]["failure_modes"] == 1
    finally:
        app.dependency_overrides.clear()
