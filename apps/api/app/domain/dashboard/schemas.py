from typing import Literal

from pydantic import BaseModel, Field


StatTone = Literal["neutral", "good", "warning", "danger"]
ActivityType = Literal["document", "graph", "asset", "alert"]
AlertSeverity = Literal["Low", "Medium", "High", "Critical"]


class DashboardStat(BaseModel):
    label: str
    value: str
    delta: str
    tone: StatTone
    trend: list[int] = Field(default_factory=list)


class DashboardActivity(BaseModel):
    id: str
    title: str
    description: str
    timestamp: str
    type: ActivityType


class DashboardAlert(BaseModel):
    id: str
    asset: str
    title: str
    severity: AlertSeverity
    timestamp: str


class DashboardUpload(BaseModel):
    id: str
    document_name: str
    status: str
    timestamp: str
    document_id: str | None = None


class DashboardAssetMetric(BaseModel):
    equipment_id: str
    name: str | None = None
    degree: int | None = None
    incident_count: int | None = None
    failure_mode_count: int | None = None
    criticality_score: int | None = None


class DashboardFailureMode(BaseModel):
    failure_mode: str
    mentions: int


class DashboardGraphCluster(BaseModel):
    label: str
    value: int


class DashboardGraphSummary(BaseModel):
    nodes: int
    relationships: int
    clusters: list[DashboardGraphCluster]


class DashboardRiskSummary(BaseModel):
    score: int
    level: AlertSeverity
    explanation: str


class DashboardQuickAction(BaseModel):
    label: str
    description: str
    path: str


class DashboardResponse(BaseModel):
    stats: list[DashboardStat]
    activities: list[DashboardActivity]
    alerts: list[DashboardAlert]
    recent_uploads: list[DashboardUpload]
    critical_equipment: list[DashboardAssetMetric]
    frequent_failure_modes: list[DashboardFailureMode]
    graph: DashboardGraphSummary
    risk: DashboardRiskSummary
    quick_actions: list[DashboardQuickAction]
