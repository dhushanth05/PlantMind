import { API_BASE_URL } from "@/lib/api-client";

import type { ApiSubgraph, EquipmentContext, GraphAnalytics, GraphOverview, GraphSearchResult } from "./types";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}

export function getGraphOverview() {
  return getJson<GraphOverview>("/graph/overview");
}

export function getGraphAnalytics() {
  return getJson<GraphAnalytics>("/graph/analytics?limit=5");
}

export function getSubgraph(nodeId: string, depth: 1 | 2) {
  return getJson<ApiSubgraph>(`/graph/subgraph/${encodeURIComponent(nodeId)}?depth=${depth}&limit=120`);
}

export function searchGraph(query: string) {
  return getJson<GraphSearchResult>(`/graph/search?q=${encodeURIComponent(query)}&limit=10&offset=0`);
}

export function getEquipmentContext(equipmentId: string) {
  return getJson<EquipmentContext>(`/graph/equipment/${encodeURIComponent(equipmentId)}?limit=25&offset=0`);
}
