import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.db.mongodb.client import mongo_database
from app.db.neo4j.graph_repository import GraphRepository
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

logger = logging.getLogger(__name__)
DEPENDENCY_TIMEOUT_SECONDS = 2.0


class DashboardService:
    def __init__(self, graph_repository: GraphRepository | None = None) -> None:
        self.db = mongo_database.database
        self.graph_repository = graph_repository or GraphRepository()

    async def get_dashboard(self) -> DashboardResponse:
        (
            graph_overview,
            most_connected_assets,
            critical_equipment,
            frequent_failure_modes,
            documents_summary,
            recent_uploads,
            incident_count,
            alert_rows,
            asset_event_count,
        ) = await asyncio.gather(
            self._safe_graph_call(self.graph_repository.get_overview, self._empty_graph_overview()),
            self._safe_graph_call(lambda: self.graph_repository.most_connected_assets(limit=5), []),
            self._safe_graph_call(lambda: self.graph_repository.critical_equipment(limit=5), []),
            self._safe_graph_call(lambda: self.graph_repository.frequent_failure_modes(limit=5), []),
            self._safe_dependency_call(self._documents_summary, {"total": 0, "processed": 0, "failed": 0, "uploaded": 0}),
            self._safe_dependency_call(self._recent_uploads, []),
            self._safe_dependency_call(lambda: self._count_collection("incidents"), 0),
            self._safe_dependency_call(self._recent_alert_rows, []),
            self._safe_dependency_call(lambda: self._count_collection("asset_events"), 0),
        )

        assets_count = self._node_type_count(graph_overview, "Equipment")
        open_alerts = len(alert_rows)
        risk = self._risk_summary(open_alerts=open_alerts, critical_equipment=critical_equipment, incident_count=incident_count)

        alerts = [self._alert_from_row(row) for row in alert_rows]
        uploads = [self._upload_from_document(document) for document in recent_uploads]

        activities = self._activities(
            uploads=uploads,
            alerts=alerts,
            graph_nodes=int(graph_overview.get("total_nodes", 0)),
            asset_event_count=asset_event_count,
        )

        return DashboardResponse(
            stats=[
                DashboardStat(
                    label="Total Documents",
                    value=self._format_count(documents_summary["total"]),
                    delta=f"{documents_summary['processed']} processed",
                    tone="good" if documents_summary["failed"] == 0 else "warning",
                    trend=self._trend_from_value(documents_summary["total"]),
                ),
                DashboardStat(
                    label="Knowledge Graph Nodes",
                    value=self._format_count(int(graph_overview.get("total_nodes", 0))),
                    delta=f"{self._format_count(int(graph_overview.get('total_relationships', 0)))} linked",
                    tone="good",
                    trend=self._trend_from_value(int(graph_overview.get("total_nodes", 0))),
                ),
                DashboardStat(
                    label="Industrial Assets",
                    value=self._format_count(assets_count),
                    delta=f"{len(critical_equipment)} critical candidates",
                    tone="warning" if critical_equipment else "neutral",
                    trend=self._trend_from_value(assets_count),
                ),
                DashboardStat(
                    label="Open Alerts",
                    value=self._format_count(open_alerts),
                    delta=f"{sum(1 for alert in alerts if alert.severity in {'High', 'Critical'})} high priority",
                    tone="danger" if any(alert.severity == "Critical" for alert in alerts) else ("warning" if alerts else "good"),
                    trend=self._trend_from_value(open_alerts),
                ),
                DashboardStat(
                    label="Risk Score",
                    value=str(risk.score),
                    delta=f"{risk.level} exposure",
                    tone="danger" if risk.level == "Critical" else ("warning" if risk.level in {"High", "Medium"} else "good"),
                    trend=self._trend_from_value(risk.score),
                ),
            ],
            activities=activities,
            alerts=alerts,
            recent_uploads=uploads,
            critical_equipment=[DashboardAssetMetric.model_validate(item) for item in critical_equipment],
            frequent_failure_modes=[DashboardFailureMode.model_validate(item) for item in frequent_failure_modes],
            graph=DashboardGraphSummary(
                nodes=int(graph_overview.get("total_nodes", 0)),
                relationships=int(graph_overview.get("total_relationships", 0)),
                clusters=self._graph_clusters(graph_overview),
            ),
            risk=risk,
            quick_actions=[
                DashboardQuickAction(label="Upload Documents", description="Ingest manuals, MOCs, incident reports", path="/documents"),
                DashboardQuickAction(label="Ask Copilot", description="Run a grounded operational query", path="/copilot"),
                DashboardQuickAction(label="Open Graph", description="Inspect entities and relationships", path="/graph"),
                DashboardQuickAction(label="Review Alerts", description="Triage high-priority signals", path="/alerts"),
            ],
        )

    async def _documents_summary(self) -> dict[str, int]:
        try:
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            ]
            rows = [row async for row in self.db.documents.aggregate(pipeline)]
            by_status = {str(row.get("_id") or "unknown"): int(row.get("count", 0)) for row in rows}
            return {
                "total": sum(by_status.values()),
                "processed": by_status.get("processed", 0),
                "failed": by_status.get("failed", 0),
                "uploaded": by_status.get("uploaded", 0),
            }
        except Exception:
            logger.exception("dashboard_documents_summary_failed")
            return {"total": 0, "processed": 0, "failed": 0, "uploaded": 0}

    async def _recent_uploads(self) -> list[dict[str, Any]]:
        try:
            cursor = (
                self.db.documents.find(
                    {},
                    {
                        "filename": 1,
                        "status": 1,
                        "upload_timestamp": 1,
                        "processed_at": 1,
                        "failed_at": 1,
                    },
                )
                .sort("upload_timestamp", -1)
                .limit(6)
            )
            return [document async for document in cursor]
        except Exception:
            logger.exception("dashboard_recent_uploads_failed")
            return []

    async def _recent_alert_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        try:
            cursor = (
                self.db.asset_events.find(
                    {"$or": [{"severity": {"$in": ["High", "Critical"]}}, {"event_type": "Incident"}]},
                    {"asset_id": 1, "title": 1, "description": 1, "severity": 1, "timestamp": 1, "event_type": 1},
                )
                .sort("timestamp", -1)
                .limit(5)
            )
            rows = [document async for document in cursor]
        except Exception:
            logger.exception("dashboard_asset_alerts_failed")

        if rows:
            return rows

        try:
            cursor = (
                self.db.incidents.find({}, {"incident_id": 1, "name": 1, "type": 1, "created_at": 1, "metadata": 1})
                .sort("created_at", -1)
                .limit(5)
            )
            return [document async for document in cursor]
        except Exception:
            logger.exception("dashboard_incident_alerts_failed")
            return []

    async def _count_collection(self, collection: str) -> int:
        try:
            return int(await self.db[collection].count_documents({}))
        except Exception:
            logger.exception("dashboard_count_failed", extra={"collection": collection})
            return 0

    async def _safe_graph_call(self, call, fallback):
        try:
            return await asyncio.wait_for(call(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except Exception:
            logger.exception("dashboard_graph_call_failed")
            return fallback

    async def _safe_dependency_call(self, call, fallback):
        try:
            return await asyncio.wait_for(call(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except Exception:
            logger.exception("dashboard_dependency_call_failed")
            return fallback

    @staticmethod
    def _empty_graph_overview() -> dict[str, Any]:
        return {"total_nodes": 0, "total_relationships": 0, "node_types": [], "relationship_types": []}

    @staticmethod
    def _node_type_count(graph_overview: dict[str, Any], node_type: str) -> int:
        for item in graph_overview.get("node_types", []):
            if item.get("type") == node_type:
                return int(item.get("count", 0))
        return 0

    @staticmethod
    def _graph_clusters(graph_overview: dict[str, Any]) -> list[DashboardGraphCluster]:
        node_types = graph_overview.get("node_types", [])
        total_nodes = max(1, int(graph_overview.get("total_nodes", 0)))
        clusters = [
            DashboardGraphCluster(label=str(item.get("type", "Unknown")), value=round(int(item.get("count", 0)) / total_nodes * 100))
            for item in node_types[:5]
        ]
        return clusters

    @staticmethod
    def _risk_summary(open_alerts: int, critical_equipment: list[dict[str, Any]], incident_count: int) -> DashboardRiskSummary:
        top_criticality = max((int(item.get("criticality_score", 0)) for item in critical_equipment), default=0)
        score = min(100, open_alerts * 12 + incident_count * 2 + top_criticality)
        if score >= 80:
            level = "Critical"
        elif score >= 60:
            level = "High"
        elif score >= 35:
            level = "Medium"
        else:
            level = "Low"
        return DashboardRiskSummary(
            score=score,
            level=level,
            explanation=f"Computed from {open_alerts} open alerts, {incident_count} incidents, and graph criticality {top_criticality}.",
        )

    @staticmethod
    def _alert_from_row(row: dict[str, Any]) -> DashboardAlert:
        severity = str(row.get("severity") or "High")
        if severity not in {"Low", "Medium", "High", "Critical"}:
            severity = "High"
        return DashboardAlert(
            id=str(row.get("_id") or row.get("incident_id") or row.get("asset_id") or "alert"),
            asset=str(row.get("asset_id") or row.get("incident_id") or "Plant"),
            title=str(row.get("title") or row.get("name") or row.get("description") or "Operational risk signal"),
            severity=severity,
            timestamp=DashboardService._relative_time(row.get("timestamp") or row.get("created_at")),
        )

    @staticmethod
    def _upload_from_document(document: dict[str, Any]) -> DashboardUpload:
        timestamp = document.get("upload_timestamp") or document.get("processed_at") or document.get("failed_at")
        return DashboardUpload(
            id=str(document.get("_id")),
            document_id=str(document.get("_id")),
            document_name=str(document.get("filename") or "Industrial document"),
            status=str(document.get("status") or "uploaded"),
            timestamp=DashboardService._relative_time(timestamp),
        )

    @staticmethod
    def _activities(
        uploads: list[DashboardUpload],
        alerts: list[DashboardAlert],
        graph_nodes: int,
        asset_event_count: int,
    ) -> list[DashboardActivity]:
        activities: list[DashboardActivity] = []
        for upload in uploads[:3]:
            activities.append(
                DashboardActivity(
                    id=f"upload-{upload.id}",
                    title=f"{upload.document_name} {upload.status}",
                    description=f"Document {upload.document_id or upload.id} is {upload.status}.",
                    timestamp=upload.timestamp,
                    type="document",
                )
            )
        for alert in alerts[:2]:
            activities.append(
                DashboardActivity(
                    id=f"alert-{alert.id}",
                    title=f"{alert.asset} risk signal",
                    description=alert.title,
                    timestamp=alert.timestamp,
                    type="alert",
                )
            )
        if graph_nodes:
            activities.append(
                DashboardActivity(
                    id="graph-summary",
                    title="Knowledge graph synchronized",
                    description=f"{DashboardService._format_count(graph_nodes)} entities available for exploration.",
                    timestamp="now",
                    type="graph",
                )
            )
        if asset_event_count:
            activities.append(
                DashboardActivity(
                    id="asset-events",
                    title="Asset history indexed",
                    description=f"{DashboardService._format_count(asset_event_count)} maintenance and inspection events available.",
                    timestamp="now",
                    type="asset",
                )
            )
        return activities[:6]

    @staticmethod
    def _trend_from_value(value: int) -> list[int]:
        if value <= 0:
            return [8, 8, 8, 8, 8, 8]
        baseline = max(8, min(78, value % 80))
        return [max(8, min(92, baseline + offset)) for offset in (-10, -4, 2, 8, 4, 12)]

    @staticmethod
    def _format_count(value: int) -> str:
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if value >= 1_000:
            return f"{value / 1_000:.1f}k"
        return str(value)

    @staticmethod
    def _relative_time(value: Any) -> str:
        if value is None:
            return "unknown"
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return value
        elif isinstance(value, datetime):
            parsed = value
        else:
            return str(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        seconds = max(0, int((datetime.now(UTC) - parsed.astimezone(UTC)).total_seconds()))
        if seconds < 60:
            return "now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} min ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hr ago"
        days = hours // 24
        return f"{days} day{'s' if days != 1 else ''} ago"
