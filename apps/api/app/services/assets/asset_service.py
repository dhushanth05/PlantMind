from app.db.mongodb.asset_repository import AssetRepository
from app.domain.assets.schemas import RelatedAsset, TimelineEvent
from app.domain.graph.schemas import AssetContext, GraphNode
from app.services.graph_explorer_service import GraphExplorerService
from app.services.search.hybrid_retriever import HybridRetriever


class AssetService:
    def __init__(
        self,
        graph_service: GraphExplorerService | None = None,
        asset_repository: AssetRepository | None = None,
        retriever: HybridRetriever | None = None,
    ) -> None:
        self.graph_service = graph_service or GraphExplorerService()
        self.asset_repository = asset_repository or AssetRepository()
        self.retriever = retriever or HybridRetriever()

    async def get_asset_context(self, asset_id: str) -> AssetContext:
        return await self.graph_service.get_asset_context(equipment_id=asset_id, limit=100, offset=0)

    async def get_maintenance_history(self, asset_id: str) -> list[TimelineEvent]:
        return await self.asset_repository.get_maintenance_history(asset_id)

    async def get_inspection_findings(self, asset_id: str) -> list[dict]:
        return await self.asset_repository.get_inspection_findings(asset_id)

    async def get_retrieval_context(self, asset_id: str):
        return await self.retriever.retrieve(
            query=f"Asset digital twin context for equipment {asset_id}: incidents maintenance procedures failure modes",
            top_k=8,
        )

    def related_assets(self, context: AssetContext, retrieval_nodes: list[GraphNode]) -> list[RelatedAsset]:
        related: dict[str, RelatedAsset] = {}
        for node in retrieval_nodes:
            if "Equipment" not in node.labels:
                continue
            equipment_id = node.properties.get("equipment_id")
            if not isinstance(equipment_id, str) or equipment_id == context.equipment.properties.get("equipment_id"):
                continue
            related[equipment_id] = RelatedAsset(
                asset_id=equipment_id,
                name=node.properties.get("name") if isinstance(node.properties.get("name"), str) else None,
                relationship="GraphContext",
                reason="Connected through shared graph context, procedures, incidents, or failure modes.",
            )
        return list(related.values())[:10]

