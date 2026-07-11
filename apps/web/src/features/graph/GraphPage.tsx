import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Maximize2, Network, Split, X } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import "@xyflow/react/dist/style.css";

import { ErrorState } from "@/components/shared/ErrorState";

import { getEquipmentContext, getGraphAnalytics, getGraphOverview, getSubgraph, searchGraph } from "./api";
import { AnalyticsSidebar } from "./components/AnalyticsSidebar";
import { FilterPanel } from "./components/FilterPanel";
import { GraphCanvas } from "./components/GraphCanvas";
import { NodeDrawer } from "./components/NodeDrawer";
import { GraphSearchBar } from "./components/SearchBar";
import { getNodeType, toReactFlowGraph } from "./graph-utils";
import type { ApiGraphNode, GraphFilters, GraphNodeType } from "./types";

const allNodeTypes: GraphNodeType[] = ["Equipment", "Document", "Incident", "Procedure", "Person", "FailureMode"];
const allRelationshipTypes = ["MENTIONED_IN", "RELATED_TO", "CAUSED_BY", "ASSIGNED_TO", "REFERENCES"];

export function GraphPage() {
  const [filters, setFilters] = useState<GraphFilters>({
    nodeTypes: allNodeTypes,
    relationshipTypes: allRelationshipTypes,
    depth: 2,
  });
  const [centerNodeId, setCenterNodeId] = useState("P204");
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>("eq-p204");
  const [searchResults, setSearchResults] = useState<ApiGraphNode[]>([]);
  const [highlightedIds, setHighlightedIds] = useState<Set<string>>(new Set());
  const [searchParams] = useSearchParams();
  const [loadedUrlQuery, setLoadedUrlQuery] = useState<string | null>(null);

  const overviewQuery = useQuery({ queryKey: ["graph", "overview"], queryFn: getGraphOverview });
  const analyticsQuery = useQuery({ queryKey: ["graph", "analytics"], queryFn: getGraphAnalytics });
  const subgraphQuery = useQuery({
    queryKey: ["graph", "subgraph", centerNodeId, filters.depth],
    queryFn: () => getSubgraph(centerNodeId, filters.depth),
  });

  const subgraph = subgraphQuery.data;
  const selectedNode = subgraph?.nodes.find((node) => node.id === selectedNodeId);
  const selectedEquipmentId =
    selectedNode && getNodeType(selectedNode) === "Equipment"
      ? String(selectedNode.properties.equipment_id ?? selectedNode.id)
      : undefined;
  const equipmentQuery = useQuery({
    queryKey: ["graph", "equipment", selectedEquipmentId],
    queryFn: () => getEquipmentContext(selectedEquipmentId ?? ""),
    enabled: Boolean(selectedEquipmentId),
  });

  useEffect(() => {
    const liveEquipmentId = analyticsQuery.data?.most_connected_assets[0]?.equipment_id;
    if (!liveEquipmentId || centerNodeId !== "P204") {
      return;
    }
    setCenterNodeId(liveEquipmentId);
    setSelectedNodeId(undefined);
  }, [analyticsQuery.data, centerNodeId]);

  const graph = useMemo(
    () => (subgraph ? toReactFlowGraph(subgraph, filters, selectedNodeId, highlightedIds) : { nodes: [], edges: [] }),
    [filters, highlightedIds, selectedNodeId, subgraph],
  );

  const selectAndExpand = useCallback((node: ApiGraphNode) => {
    setSelectedNodeId(node.id);
    setCenterNodeId(String(node.properties.equipment_id ?? node.properties.document_id ?? node.id));
    setSearchResults([]);
  }, []);

  const runSearch = useCallback(
    async (query: string) => {
      const result = await searchGraph(query);
      setSearchResults(result.nodes);
      if (result.nodes[0]) {
        selectAndExpand(result.nodes[0]);
      }
    },
    [selectAndExpand],
  );

  useEffect(() => {
    const query = searchParams.get("q")?.trim();
    if (!query || loadedUrlQuery === query) {
      return;
    }
    setLoadedUrlQuery(query);
    void runSearch(query);
  }, [loadedUrlQuery, runSearch, searchParams]);

  const expandNode = (nodeId: string) => {
    const node = subgraph?.nodes.find((item) => item.id === nodeId);
    if (!node) return;
    setSelectedNodeId(node.id);
    setCenterNodeId(String(node.properties.equipment_id ?? node.properties.document_id ?? node.id));
  };

  const highlightNeighbors = () => {
    if (!selectedNodeId) return;
    const neighborIds = new Set<string>([selectedNodeId]);
    subgraph?.relationships.forEach((relationship) => {
      if (relationship.source === selectedNodeId) neighborIds.add(relationship.target);
      if (relationship.target === selectedNodeId) neighborIds.add(relationship.source);
    });
    setHighlightedIds(neighborIds);
  };

  const resetGraph = () => {
    setCenterNodeId("P204");
    setSelectedNodeId("eq-p204");
    setHighlightedIds(new Set());
    setSearchResults([]);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      <header className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Knowledge Graph Explorer</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Industrial relationship map</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
            Explore equipment, documents, incidents, procedures, personnel, and failure modes without loading the full graph.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Metric icon={<Network className="h-4 w-4" />} label="Nodes" value={(overviewQuery.data?.total_nodes ?? 0).toLocaleString()} />
          <Metric icon={<Split className="h-4 w-4" />} label="Relationships" value={(overviewQuery.data?.total_relationships ?? 0).toLocaleString()} />
          <Metric icon={<Maximize2 className="h-4 w-4" />} label="Depth" value={`${filters.depth}-hop`} />
        </div>
      </header>

      <div className="flex gap-4">
        <aside className="hidden w-80 shrink-0 space-y-4 xl:block">
          <FilterPanel filters={filters} onChange={setFilters} />
          {highlightedIds.size ? (
            <button
              onClick={() => setHighlightedIds(new Set())}
              className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-md border border-border bg-white text-sm font-medium dark:bg-slate-950"
            >
              <X className="h-4 w-4" />
              Clear highlight
            </button>
          ) : null}
        </aside>

        <section className="relative min-w-0 flex-1">
          <GraphSearchBar onSearch={runSearch} results={searchResults} onSelect={selectAndExpand} />
          {subgraphQuery.isError ? (
            <div className="mb-3">
              <ErrorState message="Unable to load graph context from the backend. Search for a node or retry when Neo4j is available." />
            </div>
          ) : null}
          <GraphCanvas
            nodes={graph.nodes}
            edges={graph.edges}
            loading={subgraphQuery.isFetching}
            onNodeSelect={setSelectedNodeId}
            onNodeExpand={expandNode}
            onHighlightNeighbors={highlightNeighbors}
            onReset={resetGraph}
          />
          <NodeDrawer
            node={selectedNode}
            equipmentContext={equipmentQuery.data}
            onClose={() => {
              setSelectedNodeId(undefined);
              setHighlightedIds(new Set());
            }}
          />
        </section>

        <AnalyticsSidebar overview={overviewQuery.data} analytics={analyticsQuery.data} />
      </div>
    </motion.div>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="inline-flex min-w-40 items-center gap-3 rounded-md border border-border bg-white px-3 py-2 shadow-sm dark:bg-slate-950">
      <span className="text-primary">{icon}</span>
      <span>
        <span className="block text-xs text-slate-500 dark:text-slate-400">{label}</span>
        <span className="text-sm font-semibold">{value}</span>
      </span>
    </div>
  );
}
