from app.domain.graph.schemas import GraphNode
from app.domain.search.schemas import EvidenceItem, HybridGraphContext, RetrievalContext


class ContextBuilder:
    def build(self, query: str, evidence: list[EvidenceItem], graph_context: HybridGraphContext) -> RetrievalContext:
        return RetrievalContext(
            query=query,
            chunks=evidence,
            graph_context=graph_context,
            asset_context=graph_context.asset_contexts,
            incidents=self._nodes_with_label(graph_context, "Incident"),
            procedures=self._nodes_with_label(graph_context, "Procedure"),
        )

    @staticmethod
    def _nodes_with_label(graph_context: HybridGraphContext, label: str) -> list[GraphNode]:
        nodes: dict[str, GraphNode] = {}
        for node in graph_context.related_nodes:
            if label in node.labels:
                nodes[node.id] = node
        for context in graph_context.asset_contexts:
            selected = context.connected_incidents if label == "Incident" else context.related_procedures
            for node in selected:
                nodes[node.id] = node
        return list(nodes.values())

