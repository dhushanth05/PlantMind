import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.db.mongodb.client import mongo_database
from app.domain.alerts.schemas import AlertRecord, AlertSummary, AlertsDashboardResponse

logger = logging.getLogger(__name__)
DEPENDENCY_TIMEOUT_SECONDS = 2.0


class AlertsDashboardService:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def get_dashboard(self) -> AlertsDashboardResponse:
        active_rows, history_rows = await asyncio.gather(
            self._safe_call(lambda: self._alert_rows(active=True), []),
            self._safe_call(lambda: self._alert_rows(active=False), []),
        )
        active_alerts = [self._alert_from_row(row, default_status="Open") for row in active_rows]
        history = [self._alert_from_row(row, default_status="Resolved") for row in history_rows]
        return AlertsDashboardResponse(
            summary=AlertSummary(
                active=len(active_alerts),
                critical=sum(1 for alert in active_alerts if alert.severity == "Critical"),
                high=sum(1 for alert in active_alerts if alert.severity == "High"),
                resolved=sum(1 for alert in history if alert.status == "Resolved"),
            ),
            active_alerts=active_alerts,
            alert_history=history,
        )

    async def _alert_rows(self, active: bool) -> list[dict[str, Any]]:
        status_filter = {"$nin": ["Resolved", "resolved"]} if active else {"$in": ["Resolved", "resolved"]}
        rows: list[dict[str, Any]] = []
        try:
            cursor = (
                self.db.asset_events.find(
                    {
                        "$or": [{"severity": {"$in": ["Medium", "High", "Critical"]}}, {"event_type": "Incident"}],
                        "status": status_filter,
                    },
                    {"asset_id": 1, "title": 1, "description": 1, "severity": 1, "timestamp": 1, "status": 1, "failure_mode": 1},
                )
                .sort("timestamp", -1)
                .limit(50)
            )
            rows = [row async for row in cursor]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("alerts_asset_events_failed")

        if rows or not active:
            return rows

        try:
            cursor = (
                self.db.incidents.find({}, {"incident_id": 1, "name": 1, "type": 1, "created_at": 1, "metadata": 1})
                .sort("created_at", -1)
                .limit(50)
            )
            return [row async for row in cursor]
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("alerts_incidents_failed")
            return []

    async def _safe_call(self, call, fallback):
        try:
            return await asyncio.wait_for(call(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except TimeoutError:
            logger.warning("alerts_dashboard_dependency_timeout")
            return fallback
        except Exception as exc:
            logger.warning("alerts_dashboard_dependency_failed: %s", exc)
            return fallback

    @staticmethod
    def _alert_from_row(row: dict[str, Any], default_status: str) -> AlertRecord:
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        return AlertRecord(
            id=str(row.get("_id") or row.get("incident_id") or row.get("asset_id") or "alert"),
            title=str(row.get("title") or row.get("name") or row.get("description") or "Operational alert"),
            severity=AlertsDashboardService._severity(row.get("severity") or metadata.get("severity") or "High"),
            status=AlertsDashboardService._status(row.get("status") or default_status),
            asset_id=str(row.get("asset_id") or metadata.get("asset_id")) if row.get("asset_id") or metadata.get("asset_id") else None,
            failure_mode=str(row.get("failure_mode") or metadata.get("failure_mode") or row.get("type")) if row.get("failure_mode") or metadata.get("failure_mode") or row.get("type") else None,
            timestamp=AlertsDashboardService._relative_time(row.get("timestamp") or row.get("created_at")),
            description=str(row.get("description") or row.get("type") or "") or None,
            incident_id=str(row.get("incident_id")) if row.get("incident_id") else None,
        )

    @staticmethod
    def _severity(value: Any) -> str:
        text = str(value)
        return text if text in {"Low", "Medium", "High", "Critical"} else "High"

    @staticmethod
    def _status(value: Any) -> str:
        text = str(value)
        return text if text in {"Open", "Acknowledged", "Resolved"} else "Open"

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
