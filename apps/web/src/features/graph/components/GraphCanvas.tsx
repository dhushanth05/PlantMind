import { useEffect, useMemo } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type NodeMouseHandler,
} from "@xyflow/react";

import { PlantNode } from "./PlantNode";
import { GraphLoading } from "./GraphLoading";
import { Legend } from "./Legend";
import { Toolbar } from "./Toolbar";
import type { PlantGraphEdge, PlantGraphNode } from "../types";

type GraphCanvasProps = {
  nodes: PlantGraphNode[];
  edges: PlantGraphEdge[];
  loading?: boolean;
  onNodeSelect: (nodeId: string) => void;
  onNodeExpand: (nodeId: string) => void;
  onHighlightNeighbors: () => void;
  onReset: () => void;
};

const nodeTypes = { plantNode: PlantNode };

export function GraphCanvas(props: GraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

function GraphCanvasInner({
  nodes: inputNodes,
  edges: inputEdges,
  loading,
  onNodeSelect,
  onNodeExpand,
  onHighlightNeighbors,
  onReset,
}: GraphCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(inputNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(inputEdges);
  const reactFlow = useReactFlow();

  useEffect(() => {
    setNodes(inputNodes);
    setEdges(inputEdges);
    window.setTimeout(() => reactFlow.fitView({ padding: 0.18, duration: 500 }), 50);
  }, [inputNodes, inputEdges, reactFlow, setEdges, setNodes]);

  const styledEdges = useMemo(
    () =>
      edges.map((edge) => ({
        ...edge,
        className: edge.data?.dimmed ? "opacity-20" : "",
      })),
    [edges],
  );

  const handleNodeClick: NodeMouseHandler = (_, node) => onNodeSelect(node.id);
  const handleNodeDoubleClick: NodeMouseHandler = (_, node) => onNodeExpand(node.id);

  return (
    <div className="relative h-full min-h-[720px] overflow-hidden rounded-md border border-border bg-white dark:bg-slate-950">
      <Toolbar
        onZoomIn={() => reactFlow.zoomIn()}
        onZoomOut={() => reactFlow.zoomOut()}
        onFit={() => reactFlow.fitView({ padding: 0.18, duration: 500 })}
        onReset={onReset}
        onHighlightPath={onHighlightNeighbors}
      />
      <ReactFlow
        nodes={nodes.length ? nodes : inputNodes}
        edges={styledEdges.length ? styledEdges : inputEdges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        onNodeDoubleClick={handleNodeDoubleClick}
        fitView
        fitViewOptions={{ padding: 0.18 }}
        minZoom={0.2}
        maxZoom={1.8}
      >
        <Background gap={24} size={1} />
        <MiniMap pannable zoomable nodeStrokeWidth={3} className="!bg-white dark:!bg-slate-950" />
        <Controls showInteractive={false} />
      </ReactFlow>
      {loading ? <GraphLoading /> : null}
      <Legend />
    </div>
  );
}
