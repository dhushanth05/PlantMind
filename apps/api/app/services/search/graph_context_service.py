import logging

from app.domain.documents.schemas import EntityExtractionResult, EntityItem
from app.domain.graph.schemas import AssetContext, GraphNode, GraphRelationship, GraphSubgraph
from app.domain.search.schemas import HybridGraphContext
from app.services.graph_explorer_service import GraphExplorerService

logger = logging.getLogger(__name__)


class GraphContextService:
    def __init__(self, graph_service: GraphExplorerService | None = None) -> None:
        self.graph_service = graph_service or GraphExplorerService()

    async def expand(self, entities: EntityExtractionResult, depth: int = 2, limit: int = 100) -> HybridGraphContext:
        subgraphs: list[GraphSubgraph] = []
        asset_contexts: list[AssetContext] = []

        for equipment in entities.equipment:
            asset_context = await self._try_asset_context(equipment, limit=limit)
            if asset_context is not None:
                asset_contexts.append(asset_context)

            subgraph = await self._try_subgraph(equipment.id, depth=depth, limit=limit)
            if subgraph is not None:
                subgraphs.append(subgraph)

        for entity in [*entities.personnel, *entities.procedures, *entities.incidents, *entities.failure_modes]:
            subgraph = await self._try_subgraph(entity.id, depth=depth, limit=limit)
            if subgraph is not None:
                subgraphs.append(subgraph)

        return HybridGraphContext(
            subgraphs=subgraphs,
            asset_contexts=asset_contexts,
            related_nodes=self._dedupe_nodes(subgraphs, asset_contexts),
            relationships=self._dedupe_relationships(subgraphs, asset_contexts),
        )

    async def _try_asset_context(self, equipment: EntityItem, limit: int) -> AssetContext | None:
        try:
            return await self.graph_service.get_asset_context(equipment_id=equipment.id, limit=limit, offset=0)
        except LookupError:
            logger.info("asset_context_not_found", extra={"equipment_id": equipment.id})
            return None

    async def _try_subgraph(self, node_id: str, depth: int, limit: int) -> GraphSubgraph | None:
        try:
            return await self.graph_service.get_subgraph(node_id=node_id, depth=depth, limit=limit)
        except LookupError:
            logger.info("subgraph_not_found", extra={"node_id": node_id})
            return None

    @staticmethod
    def _dedupe_nodes(subgraphs: list[GraphSubgraph], asset_contexts: list[AssetContext]) -> list[GraphNode]:
        nodes: dict[str, GraphNode] = {}
        for subgraph in subgraphs:
            nodes[subgraph.center_node.id] = subgraph.center_node
            for node in subgraph.nodes:
                nodes[node.id] = node
        for context in asset_contexts:
            nodes[context.equipment.id] = context.equipment
            for node in [
                *context.connected_incidents,
                *context.connected_documents,
                *context.connected_personnel,
                *context.failure_modes,
                *context.related_procedures,
            ]:
                nodes[node.id] = node
        return list(nodes.values())

    @staticmethod
    def _dedupe_relationships(
        subgraphs: list[GraphSubgraph], asset_contexts: list[AssetContext]
    ) -> list[GraphRelationship]:
        relationships: dict[str, GraphRelationship] = {}
        for subgraph in subgraphs:
            for relationship in subgraph.relationships:
                relationships[relationship.id] = relationship
        for context in asset_contexts:
            for relationship in context.relationships:
                relationships[relationship.id] = relationship
        return list(relationships.values())

