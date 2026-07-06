import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.db.mongodb.client import mongo_database
from app.db.neo4j.graph_repository import GraphRepository
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

logger = logging.getLogger(__name__)
DEPENDENCY_TIMEOUT_SECONDS = 2.0


class RiskDashboardService:
    def __init__(self, graph_repository: GraphRepository | None = None) -> None:
        self.db = mongo_database.database
        self.graph_repository = graph_repository or GraphRepository()

    async def get_dashboard(self) -> RiskDashboardResponse:
        critical_assets, failure_modes, alerts, timeline, incident_count = await asyncio.gather(
            self._safe_call(lambda: self.graph_repository.critical_equipment(limit=8), []),
            self._safe_call(lambda: self.graph_repository.frequent_failure_modes(limit=8), []),
            self._safe_call(self._recent_alert_rows, []),
            self._safe_call(self._timeline_rows, []),
            self._safe_call(lambda: self._count_collection("incidents"), 0),
        )

        assets = [self._asset_from_graph_row(row) for row in critical_assets]
        modes = [self._failure_mode_from_graph_row(row) for row in failure_modes]
        risk_score = self._overall_score(assets=assets, alerts=alerts, incident_count=incident_count)
        level = self._level(risk_score)

        return RiskDashboardResponse(
            overall_risk=RiskSummary(
                level=level,
                score=risk_score,
                explanation=(
                    f"{level} operational risk based on {len(assets)} high-risk assets, "
                    f"{len(modes)} recurring failure modes, {len(alerts)} open alerts, and {incident_count} incidents."
                ),
                trend=self._trend_from_score(risk_score),
            ),
            risk_score=risk_score,
            high_risk_assets=assets,
            recurring_failure_modes=modes,
            alerts=[self._alert_from_row(row) for row in alerts],
            recommendations=self._recommendations(assets=assets, modes=modes, alerts=alerts),
            timeline=[self._timeline_from_row(row) for row in timeline],
            heatmap=self._heatmap(assets=assets, modes=modes),
        )

    async def _recent_alert_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        try:
            cursor = (
                self.db.asset_events.find(
                    {"$or": [{"severity": {"$in": ["High", "Critical"]}}, {"event_type": "Incident"}]},
                    {"asset_id": 1, "title": 1, "description": 1, "severity": 1, "timestamp": 1, "event_type": 1},
                )
                .sort("timestamp", -1)
                .limit(8)
            )
            rows = [document async for document in cursor]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("risk_asset_alerts_failed")

        if rows:
            return rows

        try:
            cursor = (
                self.db.incidents.find({}, {"incident_id": 1, "name": 1, "type": 1, "created_at": 1, "metadata": 1})
                .sort("created_at", -1)
                .limit(8)
            )
            return [document async for document in cursor]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("risk_incident_alerts_failed")
            return []

    async def _timeline_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        try:
            cursor = (
                self.db.asset_events.find(
                    {},
                    {"asset_id": 1, "title": 1, "description": 1, "severity": 1, "timestamp": 1, "event_type": 1},
                )
                .sort("timestamp", -1)
                .limit(10)
            )
            rows = [document async for document in cursor]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("risk_asset_timeline_failed")

        if rows:
            return rows

        try:
            cursor = (
                self.db.incidents.find({}, {"incident_id": 1, "name": 1, "type": 1, "created_at": 1, "metadata": 1})
                .sort("created_at", -1)
                .limit(10)
            )
            return [document async for document in cursor]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("risk_incident_timeline_failed")
            return []

    async def _count_collection(self, collection: str) -> int:
        try:
            return int(await self.db[collection].count_documents({}))
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("risk_count_failed", extra={"collection": collection})
            return 0

    async def _safe_call(self, call, fallback):
        try:
            return await asyncio.wait_for(call(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except TimeoutError:
            logger.warning("risk_dashboard_dependency_timeout")
            return fallback
        except Exception as exc:
            logger.warning("risk_dashboard_dependency_failed: %s", exc)
            return fallback

    @staticmethod
    def _asset_from_graph_row(row: dict[str, Any]) -> RiskAsset:
        criticality = int(row.get("criticality_score", 0) or 0)
        incident_count = int(row.get("incident_count", 0) or 0)
        failure_mode_count = int(row.get("failure_mode_count", 0) or 0)
        score = min(100, criticality + incident_count * 8 + failure_mode_count * 6)
        return RiskAsset(
            equipment_id=str(row.get("equipment_id") or "unknown"),
            name=row.get("name"),
            risk_score=score,
            risk_level=RiskDashboardService._level(score),
            incident_count=incident_count,
            failure_mode_count=failure_mode_count,
            criticality_score=criticality,
        )

    @staticmethod
    def _failure_mode_from_graph_row(row: dict[str, Any]) -> RiskFailureMode:
        mentions = int(row.get("mentions", 0) or 0)
        score = min(100, mentions * 12)
        return RiskFailureMode(
            failure_mode=str(row.get("failure_mode") or "Unknown failure mode"),
            mentions=mentions,
            severity=RiskDashboardService._level(score),
            last_seen=None,
        )

    @staticmethod
    def _alert_from_row(row: dict[str, Any]) -> RiskAlert:
        severity = RiskDashboardService._normalize_level(row.get("severity") or "High")
        return RiskAlert(
            id=str(row.get("_id") or row.get("incident_id") or row.get("asset_id") or "alert"),
            asset_id=str(row.get("asset_id")) if row.get("asset_id") else None,
            title=str(row.get("title") or row.get("name") or row.get("description") or "Operational risk alert"),
            severity=severity,
            timestamp=RiskDashboardService._relative_time(row.get("timestamp") or row.get("created_at")),
            incident_id=str(row.get("incident_id")) if row.get("incident_id") else None,
        )

    @staticmethod
    def _timeline_from_row(row: dict[str, Any]) -> RiskTimelineEvent:
        severity = RiskDashboardService._normalize_level(row.get("severity") or "Medium")
        return RiskTimelineEvent(
            id=str(row.get("_id") or row.get("incident_id") or row.get("asset_id") or "event"),
            title=str(row.get("title") or row.get("name") or "Operational risk event"),
            description=str(row.get("description") or row.get("type") or "Risk event captured from operational evidence."),
            event_type=str(row.get("event_type") or row.get("type") or "Incident"),
            severity=severity,
            timestamp=RiskDashboardService._relative_time(row.get("timestamp") or row.get("created_at")),
            asset_id=str(row.get("asset_id")) if row.get("asset_id") else None,
            incident_id=str(row.get("incident_id")) if row.get("incident_id") else None,
        )

    @staticmethod
    def _recommendations(assets: list[RiskAsset], modes: list[RiskFailureMode], alerts: list[dict[str, Any]]) -> list[RiskRecommendation]:
        recommendations: list[RiskRecommendation] = []
        for asset in assets[:3]:
            recommendations.append(
                RiskRecommendation(
                    id=f"asset-{asset.equipment_id}",
                    title=f"Review risk drivers for {asset.name or asset.equipment_id}",
                    rationale=(
                        f"{asset.incident_count} incidents and {asset.failure_mode_count} failure modes are contributing "
                        f"to a {asset.risk_level} asset risk score."
                    ),
                    priority=asset.risk_level,
                    asset_id=asset.equipment_id,
                    copilot_query=f"Explain the risk drivers for {asset.equipment_id}",
                )
            )
        for mode in modes[:2]:
            recommendations.append(
                RiskRecommendation(
                    id=f"failure-{mode.failure_mode}",
                    title=f"Investigate recurring {mode.failure_mode}",
                    rationale=f"{mode.failure_mode} appears {mode.mentions} times in the graph context.",
                    priority=mode.severity,
                    copilot_query=f"What procedures mitigate {mode.failure_mode}?",
                )
            )
        if alerts and not recommendations:
            alert = RiskDashboardService._alert_from_row(alerts[0])
            recommendations.append(
                RiskRecommendation(
                    id=f"alert-{alert.id}",
                    title=f"Triage {alert.title}",
                    rationale="Open high-severity alerts should be reviewed before restart or handover.",
                    priority=alert.severity,
                    asset_id=alert.asset_id,
                    copilot_query=f"What evidence explains alert {alert.title}?",
                )
            )
        return recommendations[:5]

    @staticmethod
    def _heatmap(assets: list[RiskAsset], modes: list[RiskFailureMode]) -> list[RiskHeatmapCell]:
        if not assets or not modes:
            return []
        cells: list[RiskHeatmapCell] = []
        for asset in assets[:5]:
            for mode in modes[:4]:
                score = min(100, round(asset.risk_score * 0.65 + min(100, mode.mentions * 10) * 0.35))
                cells.append(
                    RiskHeatmapCell(
                        asset_id=asset.equipment_id,
                        asset_name=asset.name,
                        failure_mode=mode.failure_mode,
                        score=score,
                        level=RiskDashboardService._level(score),
                    )
                )
        return cells

    @staticmethod
    def _overall_score(assets: list[RiskAsset], alerts: list[dict[str, Any]], incident_count: int) -> int:
        top_asset = max((asset.risk_score for asset in assets), default=0)
        critical_alerts = sum(1 for alert in alerts if RiskDashboardService._normalize_level(alert.get("severity") or "High") == "Critical")
        high_alerts = len(alerts)
        return min(100, top_asset + critical_alerts * 8 + high_alerts * 4 + incident_count * 2)

    @staticmethod
    def _trend_from_score(score: int) -> list[int]:
        if score <= 0:
            return [8, 8, 8, 8, 8, 8]
        return [max(5, min(100, score + offset)) for offset in (-18, -12, -8, -2, 3, 0)]

    @staticmethod
    def _level(score: int) -> str:
        if score >= 80:
            return "Critical"
        if score >= 55:
            return "High"
        if score >= 30:
            return "Medium"
        return "Low"

    @staticmethod
    def _normalize_level(value: Any) -> str:
        text = str(value)
        return text if text in {"Low", "Medium", "High", "Critical"} else "High"

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
