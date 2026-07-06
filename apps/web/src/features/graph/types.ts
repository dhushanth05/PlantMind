import type { Edge, Node } from "@xyflow/react";

export type GraphNodeType = "Equipment" | "Document" | "Incident" | "Procedure" | "Person" | "FailureMode";

export type ApiGraphNode = {
  id: string;
  labels: string[];
  properties: Record<string, unknown>;
};

export type ApiGraphRelationship = {
  id: string;
  type: string;
  source: string;
  target: string;
  properties: Record<string, unknown>;
};

export type ApiSubgraph = {
  center_node: ApiGraphNode;
  nodes: ApiGraphNode[];
  relationships: ApiGraphRelationship[];
};

export type GraphOverview = {
  total_nodes: number;
  total_relationships: number;
  node_types: { type: string; count: number }[];
  relationship_types: { type: string; count: number }[];
};

export type GraphSearchResult = {
  nodes: ApiGraphNode[];
  total: number;
  limit: number;
  offset: number;
};

export type EquipmentContext = {
  equipment: ApiGraphNode;
  connected_incidents: ApiGraphNode[];
  connected_documents: ApiGraphNode[];
  connected_personnel: ApiGraphNode[];
  failure_modes: ApiGraphNode[];
  related_procedures: ApiGraphNode[];
  relationships: ApiGraphRelationship[];
};

export type GraphAnalytics = {
  most_connected_assets: { equipment_id: string; name?: string | null; degree: number }[];
  critical_equipment: {
    equipment_id: string;
    name?: string | null;
    incident_count: number;
    failure_mode_count: number;
    degree: number;
    criticality_score: number;
  }[];
  frequent_failure_modes: { failure_mode: string; mentions: number }[];
};

export type PlantGraphNodeData = {
  apiNode: ApiGraphNode;
  type: GraphNodeType;
  label: string;
  subtitle: string;
  highlighted?: boolean;
  dimmed?: boolean;
};

export type PlantGraphNode = Node<PlantGraphNodeData>;
export type PlantGraphEdge = Edge<{ relationship: ApiGraphRelationship; highlighted?: boolean; dimmed?: boolean }>;

export type GraphFilters = {
  nodeTypes: GraphNodeType[];
  relationshipTypes: string[];
  depth: 1 | 2;
};

