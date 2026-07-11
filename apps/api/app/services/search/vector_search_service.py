import logging

from app.db.mongodb.vector_repository import VectorSearchRepository
from app.domain.search.schemas import VectorSearchHit
from app.services.ai.embedding.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorSearchService:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        repository: VectorSearchRepository | None = None,
    ) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.repository = repository or VectorSearchRepository()

    async def embed_query(self, query: str) -> list[float]:
        return await self.embedding_service.embed_query(query)

    async def search(self, query: str, query_embedding: list[float], top_k: int) -> list[VectorSearchHit]:
        results = await self.repository.search_chunks(query=query, query_embedding=query_embedding, top_k=top_k)
        logger.info("vector_search_complete", extra={"hits": len(results), "top_k": top_k})
        return results
