from typing import Any

from pydantic import BaseModel, Field


class GraphTypeCount(BaseModel):
    type: str
    count: int


class GraphOverview(BaseModel):
    total_nodes: int
    total_relationships: int
    node_types: list[GraphTypeCount]
    relationship_types: list[GraphTypeCount]


class GraphNode(BaseModel):
    id: str
    labels: list[str]
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    id: str
    type: str
    source: str
    target: str
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphSubgraph(BaseModel):
    center_node: GraphNode
    nodes: list[GraphNode]
    relationships: list[GraphRelationship]


class GraphSearchResult(BaseModel):
    nodes: list[GraphNode]
    total: int
    limit: int
    offset: int


class AssetContext(BaseModel):
    equipment: GraphNode
    connected_incidents: list[GraphNode]
    connected_documents: list[GraphNode]
    connected_personnel: list[GraphNode]
    failure_modes: list[GraphNode]
    related_procedures: list[GraphNode]
    relationships: list[GraphRelationship]


class ConnectedAssetMetric(BaseModel):
    equipment_id: str
    name: str | None = None
    degree: int


class CriticalEquipmentMetric(BaseModel):
    equipment_id: str
    name: str | None = None
    incident_count: int
    failure_mode_count: int
    degree: int
    criticality_score: int


class FailureModeMetric(BaseModel):
    failure_mode: str
    mentions: int


class GraphAnalytics(BaseModel):
    most_connected_assets: list[ConnectedAssetMetric]
    critical_equipment: list[CriticalEquipmentMetric]
    frequent_failure_modes: list[FailureModeMetric]

