from typing import Literal

from pydantic import BaseModel


AlertSeverity = Literal["Low", "Medium", "High", "Critical"]
AlertStatus = Literal["Open", "Acknowledged", "Resolved"]


class AlertRecord(BaseModel):
    id: str
    title: str
    severity: AlertSeverity
    status: AlertStatus
    asset_id: str | None = None
    failure_mode: str | None = None
    timestamp: str
    description: str | None = None
    incident_id: str | None = None


class AlertSummary(BaseModel):
    active: int
    critical: int
    high: int
    resolved: int


class AlertsDashboardResponse(BaseModel):
    summary: AlertSummary
    active_alerts: list[AlertRecord]
    alert_history: list[AlertRecord]
