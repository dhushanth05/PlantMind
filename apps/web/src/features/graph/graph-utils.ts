import { MarkerType, type NodeProps } from "@xyflow/react";
import { AlertTriangle, FileText, Settings2, UserRound, Wrench, Workflow } from "lucide-react";

import type {
  ApiGraphNode,
  ApiSubgraph,
  GraphFilters,
  GraphNodeType,
  PlantGraphEdge,
  PlantGraphNode,
} from "./types";

export const nodeTypeConfig: Record<GraphNodeType, { color: string; bg: string; icon: typeof Wrench }> = {
  Equipment: { color: "#0f766e", bg: "#ccfbf1", icon: Wrench },
  Document: { color: "#2563eb", bg: "#dbeafe", icon: FileText },
  Incident: { color: "#dc2626", bg: "#fee2e2", icon: AlertTriangle },
  Procedure: { color: "#7c3aed", bg: "#ede9fe", icon: Workflow },
  Person: { color: "#475569", bg: "#e2e8f0", icon: UserRound },
  FailureMode: { color: "#d97706", bg: "#fef3c7", icon: Settings2 },
};

export function getNodeType(node: ApiGraphNode): GraphNodeType {
  const label = node.labels.find((item) => item === "FailureMode" || item === "Equipment" || item === "Document" || item === "Incident" || item === "Procedure" || item === "Person");
  return (label ?? "Document") as GraphNodeType;
}

export function getNodeLabel(node: ApiGraphNode): string {
  const properties = node.properties;
  return String(
    properties.name ??
      properties.equipment_id ??
      properties.document_id ??
      properties.incident_id ??
      properties.procedure_id ??
      properties.person_id ??
      properties.failure_mode_id ??
      node.id,
  );
}

export function getNodeSubtitle(node: ApiGraphNode): string {
  const type = getNodeType(node);
  const properties = node.properties;
  if (type === "Document") return String(properties.filename ?? properties.document_id ?? "Document");
  if (type === "Equipment") return String(properties.type ?? "Industrial asset");
  if (type === "Person") return String(properties.role ?? "Personnel");
  if (type === "Incident") return String(properties.severity ?? "Incident");
  return type;
}

export function toReactFlowGraph(
  subgraph: ApiSubgraph,
  filters: GraphFilters,
  selectedNodeId?: string,
  highlightedIds: Set<string> = new Set(),
): { nodes: PlantGraphNode[]; edges: PlantGraphEdge[] } {
  const allowedNodeTypes = new Set(filters.nodeTypes);
  const allowedRelationshipTypes = new Set(filters.relationshipTypes);
  const filteredNodes = subgraph.nodes.filter((node) => allowedNodeTypes.has(getNodeType(node)));
  const nodeIds = new Set(filteredNodes.map((node) => node.id));
  const filteredRelationships = subgraph.relationships.filter(
    (relationship) =>
      nodeIds.has(relationship.source) &&
      nodeIds.has(relationship.target) &&
      (allowedRelationshipTypes.size === 0 || allowedRelationshipTypes.has(relationship.type)),
  );
  const positions = radialLayout(filteredNodes, subgraph.center_node.id);
  const hasHighlight = highlightedIds.size > 0;

  return {
    nodes: filteredNodes.map((node) => ({
      id: node.id,
      type: "plantNode",
      position: positions[node.id] ?? { x: 0, y: 0 },
      data: {
        apiNode: node,
        type: getNodeType(node),
        label: getNodeLabel(node),
        subtitle: getNodeSubtitle(node),
        highlighted: highlightedIds.has(node.id) || node.id === selectedNodeId,
        dimmed: hasHighlight && !highlightedIds.has(node.id) && node.id !== selectedNodeId,
      },
      selected: node.id === selectedNodeId,
    })),
    edges: filteredRelationships.map((relationship) => ({
      id: relationship.id,
      source: relationship.source,
      target: relationship.target,
      label: relationship.type,
      animated: highlightedIds.has(relationship.source) || highlightedIds.has(relationship.target),
      markerEnd: { type: MarkerType.ArrowClosed },
      data: {
        relationship,
        highlighted: highlightedIds.has(relationship.source) || highlightedIds.has(relationship.target),
        dimmed:
          hasHighlight && !highlightedIds.has(relationship.source) && !highlightedIds.has(relationship.target),
      },
      style: {
        stroke:
          highlightedIds.has(relationship.source) || highlightedIds.has(relationship.target)
            ? "#0f766e"
            : "#94a3b8",
        strokeWidth:
          highlightedIds.has(relationship.source) || highlightedIds.has(relationship.target) ? 2.2 : 1.2,
      },
    })),
  };
}

function radialLayout(nodes: ApiGraphNode[], centerId: string): Record<string, { x: number; y: number }> {
  const positions: Record<string, { x: number; y: number }> = {};
  const center = nodes.find((node) => node.id === centerId) ?? nodes[0];
  if (!center) return positions;
  positions[center.id] = { x: 0, y: 0 };
  const others = nodes.filter((node) => node.id !== center.id);
  const radius = Math.max(260, others.length * 26);
  others.forEach((node, index) => {
    const angle = (index / Math.max(others.length, 1)) * Math.PI * 2;
    const tier = index % 3 === 0 ? 1.2 : index % 2 === 0 ? 0.9 : 1;
    positions[node.id] = {
      x: Math.cos(angle) * radius * tier,
      y: Math.sin(angle) * radius * tier,
    };
  });
  return positions;
}

export type PlantNodeProps = NodeProps<PlantGraphNode>;
