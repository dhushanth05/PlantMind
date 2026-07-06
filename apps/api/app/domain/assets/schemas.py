from typing import Any, Literal

from pydantic import BaseModel, Field

from app.domain.graph.schemas import GraphNode


RiskLevel = Literal["Low", "Medium", "High", "Critical"]


class HealthScore(BaseModel):
    score: int = Field(ge=0, le=100)
    status: str


class RiskAssessment(BaseModel):
    level: RiskLevel
    explanation: str
    score: int = Field(ge=0, le=100)


class TimelineEvent(BaseModel):
    event_type: Literal["Inspection", "Maintenance", "Incident", "Repair", "Recommendation"]
    title: str
    description: str
    timestamp: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphSummary(BaseModel):
    connected_nodes: int
    connected_documents: int
    connected_engineers: int
    failure_modes: int
    procedures: int


class DigitalTwinRecommendation(BaseModel):
    title: str
    rationale: str
    priority: RiskLevel


class RelatedAsset(BaseModel):
    asset_id: str
    name: str | None = None
    relationship: str
    reason: str


class AssetDigitalTwin(BaseModel):
    asset: GraphNode
    health_score: HealthScore
    risk_level: RiskAssessment
    maintenance_history: list[TimelineEvent]
    incidents: list[GraphNode]
    connected_documents: list[GraphNode]
    procedures: list[GraphNode]
    assigned_personnel: list[GraphNode]
    failure_modes: list[GraphNode]
    recommendations: list[DigitalTwinRecommendation]
    graph_summary: GraphSummary
    related_assets: list[RelatedAsset]
    operational_timeline: list[TimelineEvent]

