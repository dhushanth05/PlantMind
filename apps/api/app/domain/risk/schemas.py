from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["Low", "Medium", "High", "Critical"]


class RiskSummary(BaseModel):
    level: RiskLevel
    score: int = Field(ge=0, le=100)
    explanation: str
    trend: list[int] = Field(default_factory=list)


class RiskAsset(BaseModel):
    equipment_id: str
    name: str | None = None
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    incident_count: int = 0
    failure_mode_count: int = 0
    criticality_score: int = 0


class RiskFailureMode(BaseModel):
    failure_mode: str
    mentions: int
    severity: RiskLevel
    last_seen: str | None = None


class RiskAlert(BaseModel):
    id: str
    asset_id: str | None = None
    title: str
    severity: RiskLevel
    timestamp: str
    incident_id: str | None = None


class RiskRecommendation(BaseModel):
    id: str
    title: str
    rationale: str
    priority: RiskLevel
    asset_id: str | None = None
    copilot_query: str


class RiskTimelineEvent(BaseModel):
    id: str
    title: str
    description: str
    event_type: str
    severity: RiskLevel
    timestamp: str
    asset_id: str | None = None
    incident_id: str | None = None


class RiskHeatmapCell(BaseModel):
    asset_id: str
    asset_name: str | None = None
    failure_mode: str
    score: int = Field(ge=0, le=100)
    level: RiskLevel


class RiskDashboardResponse(BaseModel):
    overall_risk: RiskSummary
    risk_score: int = Field(ge=0, le=100)
    high_risk_assets: list[RiskAsset]
    recurring_failure_modes: list[RiskFailureMode]
    alerts: list[RiskAlert]
    recommendations: list[RiskRecommendation]
    timeline: list[RiskTimelineEvent]
    heatmap: list[RiskHeatmapCell]
