import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.risk import get_risk_dashboard_service
from app.domain.risk.schemas import (
    RiskAlert,
    RiskAsset,
    RiskDashboardResponse,
    RiskFailureMode,
    RiskHeatmapCell,
    RiskRecommendation,
    RiskSummary,
    RiskTimelineEvent,
)
from app.main import app
from app.services import risk_dashboard_service as risk_dashboard_service_module
from app.services.risk_dashboard_service import RiskDashboardService


class FakeRiskDashboardService:
    async def get_dashboard(self) -> RiskDashboardResponse:
        return RiskDashboardResponse(
            overall_risk=RiskSummary(level="High", score=72, explanation="Test risk.", trend=[50, 58, 72]),
            risk_score=72,
            high_risk_assets=[
                RiskAsset(
                    equipment_id="P204",
                    name="Pump P204",
                    risk_score=82,
                    risk_level="Critical",
                    incident_count=2,
                    failure_mode_count=1,
                    criticality_score=40,
                )
            ],
            recurring_failure_modes=[RiskFailureMode(failure_mode="Seal Leakage", mentions=4, severity="Medium")],
            alerts=[RiskAlert(id="alert-1", asset_id="P204", title="Seal alert", severity="High", timestamp="now")],
            recommendations=[
                RiskRecommendation(
                    id="rec-1",
                    title="Inspect Pump P204",
                    rationale="Recurring seal evidence.",
                    priority="High",
                    asset_id="P204",
                    copilot_query="Explain P204 risk",
                )
            ],
            timeline=[
                RiskTimelineEvent(
                    id="event-1",
                    title="Incident captured",
                    description="Seal leakage event.",
                    event_type="Incident",
                    severity="High",
                    timestamp="now",
                    asset_id="P204",
                )
            ],
            heatmap=[RiskHeatmapCell(asset_id="P204", asset_name="Pump P204", failure_mode="Seal Leakage", score=84, level="Critical")],
        )


class SlowGraphRepository:
    async def critical_equipment(self, limit: int):
        await asyncio.sleep(1)
        return [{"equipment_id": "P204", "criticality_score": 99}]

    async def frequent_failure_modes(self, limit: int):
        await asyncio.sleep(1)
        return [{"failure_mode": "Seal Leakage", "mentions": 99}]


def test_risk_dashboard_route_returns_payload() -> None:
    app.dependency_overrides[get_risk_dashboard_service] = lambda: FakeRiskDashboardService()
    try:
        client = TestClient(app)

        response = client.get("/api/v1/risk/dashboard")

        assert response.status_code == 200
        payload = response.json()
        assert payload["risk_score"] == 72
        assert payload["high_risk_assets"][0]["equipment_id"] == "P204"
        assert payload["recurring_failure_modes"][0]["failure_mode"] == "Seal Leakage"
        assert payload["heatmap"][0]["level"] == "Critical"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_risk_dashboard_returns_partial_payload_when_dependencies_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(risk_dashboard_service_module, "DEPENDENCY_TIMEOUT_SECONDS", 0.01)
    service = RiskDashboardService(graph_repository=SlowGraphRepository())

    async def slow_alerts():
        await asyncio.sleep(1)
        return [{"asset_id": "P204", "title": "Late alert", "severity": "Critical"}]

    async def slow_timeline():
        await asyncio.sleep(1)
        return [{"asset_id": "P204", "title": "Late event", "severity": "High"}]

    async def slow_count(collection: str):
        await asyncio.sleep(1)
        return 99

    monkeypatch.setattr(service, "_recent_alert_rows", slow_alerts)
    monkeypatch.setattr(service, "_timeline_rows", slow_timeline)
    monkeypatch.setattr(service, "_count_collection", slow_count)

    result = await service.get_dashboard()

    assert result.risk_score == 0
    assert result.high_risk_assets == []
    assert result.alerts == []
    assert result.timeline == []
