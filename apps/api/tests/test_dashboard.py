import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.dashboard import get_dashboard_service
from app.domain.dashboard.schemas import (
    DashboardActivity,
    DashboardAlert,
    DashboardAssetMetric,
    DashboardFailureMode,
    DashboardGraphCluster,
    DashboardGraphSummary,
    DashboardQuickAction,
    DashboardResponse,
    DashboardRiskSummary,
    DashboardStat,
    DashboardUpload,
)
from app.main import app
from app.services import dashboard_service as dashboard_service_module
from app.services.dashboard_service import DashboardService


class FakeDashboardService:
    async def get_dashboard(self) -> DashboardResponse:
        return DashboardResponse(
            stats=[
                DashboardStat(label="Total Documents", value="12", delta="10 processed", tone="good", trend=[8, 12, 16]),
                DashboardStat(label="Knowledge Graph Nodes", value="120", delta="300 linked", tone="good", trend=[20, 30, 40]),
            ],
            activities=[
                DashboardActivity(
                    id="activity-1",
                    title="Manual uploaded",
                    description="Document doc-1 is processed.",
                    timestamp="now",
                    type="document",
                )
            ],
            alerts=[
                DashboardAlert(
                    id="alert-1",
                    asset="P204",
                    title="Repeated seal leakage",
                    severity="Critical",
                    timestamp="5 min ago",
                )
            ],
            recent_uploads=[
                DashboardUpload(
                    id="doc-1",
                    document_id="doc-1",
                    document_name="pump-manual.pdf",
                    status="processed",
                    timestamp="now",
                )
            ],
            critical_equipment=[
                DashboardAssetMetric(
                    equipment_id="P204",
                    name="Pump P204",
                    degree=7,
                    incident_count=2,
                    failure_mode_count=1,
                    criticality_score=20,
                )
            ],
            frequent_failure_modes=[DashboardFailureMode(failure_mode="Seal Leakage", mentions=4)],
            graph=DashboardGraphSummary(
                nodes=120,
                relationships=300,
                clusters=[DashboardGraphCluster(label="Equipment", value=40)],
            ),
            risk=DashboardRiskSummary(
                score=78,
                level="High",
                explanation="Computed from test data.",
            ),
            quick_actions=[
                DashboardQuickAction(label="Upload Documents", description="Ingest files", path="/documents"),
            ],
        )


class SlowGraphRepository:
    async def get_overview(self):
        await asyncio.sleep(1)
        return {"total_nodes": 99, "total_relationships": 99, "node_types": [], "relationship_types": []}

    async def most_connected_assets(self, limit: int):
        await asyncio.sleep(1)
        return [{"equipment_id": "P204", "name": "Pump P204", "degree": 99}]

    async def critical_equipment(self, limit: int):
        await asyncio.sleep(1)
        return [{"equipment_id": "P204", "name": "Pump P204", "criticality_score": 99}]

    async def frequent_failure_modes(self, limit: int):
        await asyncio.sleep(1)
        return [{"failure_mode": "Seal Leakage", "mentions": 99}]


def test_dashboard_route_returns_optimized_payload() -> None:
    app.dependency_overrides[get_dashboard_service] = lambda: FakeDashboardService()
    try:
        client = TestClient(app)

        response = client.get("/api/v1/dashboard")

        assert response.status_code == 200
        payload = response.json()
        assert payload["stats"][0]["label"] == "Total Documents"
        assert payload["graph"]["nodes"] == 120
        assert payload["recent_uploads"][0]["document_name"] == "pump-manual.pdf"
        assert payload["critical_equipment"][0]["equipment_id"] == "P204"
        assert payload["frequent_failure_modes"][0]["failure_mode"] == "Seal Leakage"
        assert payload["quick_actions"][0]["path"] == "/documents"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dashboard_service_returns_partial_payload_when_dependencies_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dashboard_service_module, "DEPENDENCY_TIMEOUT_SECONDS", 0.01)
    service = DashboardService(graph_repository=SlowGraphRepository())

    async def slow_documents_summary():
        await asyncio.sleep(1)
        return {"total": 99, "processed": 99, "failed": 0, "uploaded": 0}

    async def slow_recent_uploads():
        await asyncio.sleep(1)
        return [{"filename": "pump.pdf", "status": "processed"}]

    async def slow_recent_alert_rows():
        await asyncio.sleep(1)
        return [{"asset_id": "P204", "title": "Late alert", "severity": "Critical"}]

    async def slow_count_collection(collection: str):
        await asyncio.sleep(1)
        return 99

    monkeypatch.setattr(service, "_documents_summary", slow_documents_summary)
    monkeypatch.setattr(service, "_recent_uploads", slow_recent_uploads)
    monkeypatch.setattr(service, "_recent_alert_rows", slow_recent_alert_rows)
    monkeypatch.setattr(service, "_count_collection", slow_count_collection)

    result = await service.get_dashboard()

    assert result.stats[0].value == "0"
    assert result.graph.nodes == 0
    assert result.alerts == []
    assert result.recent_uploads == []
