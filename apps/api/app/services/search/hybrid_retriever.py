import logging

from app.core.config import settings
from app.domain.search.schemas import QueryAnalysis, RetrievalContext
from app.services.ai.entity_extraction.entity_extraction_service import EntityExtractionService
from app.services.search.context_builder import ContextBuilder
from app.services.search.graph_context_service import GraphContextService
from app.services.search.ranking_service import RankingService
from app.services.search.vector_search_service import VectorSearchService

logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(
        self,
        vector_search: VectorSearchService | None = None,
        entity_extraction: EntityExtractionService | None = None,
        graph_context: GraphContextService | None = None,
        ranking: RankingService | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.vector_search = vector_search or VectorSearchService()
        self.entity_extraction = entity_extraction or EntityExtractionService()
        self.graph_context = graph_context or GraphContextService()
        self.ranking = ranking or RankingService()
        self.context_builder = context_builder or ContextBuilder()

    async def retrieve(self, query: str, top_k: int | None = None) -> RetrievalContext:
        effective_top_k = top_k or settings.hybrid_search_top_k
        query_embedding = await self.vector_search.embed_query(query)
        entities = await self.entity_extraction.extract(query)
        analysis = QueryAnalysis(query=query, embedding=query_embedding, entities=entities)

        hits = await self.vector_search.search(query_embedding=analysis.embedding, top_k=effective_top_k * 2)
        graph_context = await self.graph_context.expand(analysis.entities, depth=2, limit=100)
        evidence = self.ranking.rank(
            hits=hits,
            entities=analysis.entities,
            graph_context=graph_context,
            top_k=effective_top_k,
        )
        context = self.context_builder.build(query=query, evidence=evidence, graph_context=graph_context)
        logger.info(
            "hybrid_retrieval_complete",
            extra={
                "evidence": len(context.chunks),
                "graph_nodes": len(context.graph_context.related_nodes),
                "asset_contexts": len(context.asset_context),
            },
        )
        return context

