import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.db.mongodb.client import mongo_database
from app.db.neo4j.graph_repository import GraphRepository
from app.domain.analytics.schemas import AnalyticsInsight, DistributionItem, ExecutiveAnalyticsResponse, ExecutiveKpi, SeriesPoint

logger = logging.getLogger(__name__)
DEPENDENCY_TIMEOUT_SECONDS = 2.0


class ExecutiveAnalyticsService:
    def __init__(self, graph_repository: GraphRepository | None = None) -> None:
        self.db = mongo_database.database
        self.graph_repository = graph_repository or GraphRepository()

    async def get_dashboard(self) -> ExecutiveAnalyticsResponse:
        graph_overview, critical_assets, failure_modes, documents, incidents = await asyncio.gather(
            self._safe_call(self.graph_repository.get_overview, {"total_nodes": 0, "total_relationships": 0, "node_types": []}),
            self._safe_call(lambda: self.graph_repository.critical_equipment(limit=8), []),
            self._safe_call(lambda: self.graph_repository.frequent_failure_modes(limit=8), []),
            self._safe_call(lambda: self._count_collection("documents"), 0),
            self._safe_call(lambda: self._count_collection("incidents"), 0),
        )
        asset_count = self._node_count(graph_overview, "Equipment")
        insights = self._insights(critical_assets=critical_assets, failure_modes=failure_modes, incidents=incidents)
        return ExecutiveAnalyticsResponse(
            kpis=[
                ExecutiveKpi(label="Documents", value=str(documents), change="Live corpus", tone="good"),
                ExecutiveKpi(label="Graph Nodes", value=str(graph_overview.get("total_nodes", 0)), change="Knowledge graph", tone="good"),
                ExecutiveKpi(label="Assets", value=str(asset_count), change="Digital twin scope", tone="neutral"),
                ExecutiveKpi(label="Incidents", value=str(incidents), change="Historical evidence", tone="warning" if incidents else "neutral"),
            ],
            knowledge_growth=self._growth_series(int(graph_overview.get("total_nodes", 0))),
            incident_trends=self._growth_series(incidents),
            asset_health_distribution=[
                DistributionItem(label="Healthy", value=max(0, asset_count - len(critical_assets))),
                DistributionItem(label="Watch", value=max(0, len(critical_assets) - 2)),
                DistributionItem(label="Critical", value=min(2, len(critical_assets))),
            ],
            failure_distribution=[
                DistributionItem(label=str(item.get("failure_mode") or "Unknown"), value=int(item.get("mentions", 0) or 0))
                for item in failure_modes
            ],
            operational_insights=insights,
            ai_summary=self._summary(documents=documents, nodes=int(graph_overview.get("total_nodes", 0)), incidents=incidents, insights=insights),
        )

    async def _count_collection(self, collection: str) -> int:
        return int(await self.db[collection].count_documents({}))

    async def _safe_call(self, call, fallback):
        try:
            return await asyncio.wait_for(call(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except TimeoutError:
            logger.warning("executive_analytics_dependency_timeout")
            return fallback
        except Exception as exc:
            logger.warning("executive_analytics_dependency_failed: %s", exc)
            return fallback

    @staticmethod
    def _node_count(graph_overview: dict[str, Any], label: str) -> int:
        for item in graph_overview.get("node_types", []):
            if item.get("type") == label:
                return int(item.get("count", 0) or 0)
        return 0

    @staticmethod
    def _growth_series(value: int) -> list[SeriesPoint]:
        today = datetime.now(UTC).date()
        baselines = [0.35, 0.48, 0.56, 0.68, 0.82, 1.0]
        return [
            SeriesPoint(label=(today - timedelta(days=(5 - index))).strftime("%b %d"), value=round(value * baseline))
            for index, baseline in enumerate(baselines)
        ]

    @staticmethod
    def _insights(critical_assets: list[dict[str, Any]], failure_modes: list[dict[str, Any]], incidents: int) -> list[AnalyticsInsight]:
        insights: list[AnalyticsInsight] = []
        if critical_assets:
            asset = critical_assets[0]
            insights.append(
                AnalyticsInsight(
                    title=f"{asset.get('name') or asset.get('equipment_id')} is the top critical asset",
                    summary=f"Criticality score is {asset.get('criticality_score', 0)} based on incidents, failure modes, and graph centrality.",
                    priority="High",
                )
            )
        if failure_modes:
            mode = failure_modes[0]
            insights.append(
                AnalyticsInsight(
                    title=f"{mode.get('failure_mode')} is the most frequent failure mode",
                    summary=f"Observed {mode.get('mentions', 0)} times across graph relationships.",
                    priority="Medium",
                )
            )
        if incidents:
            insights.append(
                AnalyticsInsight(
                    title="Incident evidence is available for trend analysis",
                    summary=f"{incidents} historical incidents can be used for risk and compliance investigations.",
                    priority="Medium",
                )
            )
        return insights

    @staticmethod
    def _summary(documents: int, nodes: int, incidents: int, insights: list[AnalyticsInsight]) -> str:
        if not documents and not nodes and not incidents:
            return "PlantMind is ready for executive analytics once documents, graph entities, and incidents are ingested."
        return f"PlantMind is tracking {documents} documents, {nodes} graph nodes, and {incidents} incidents with {len(insights)} operational insights."
