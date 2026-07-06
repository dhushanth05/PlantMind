import hashlib
import logging

from app.core.config import settings
from app.db.redis.cache import RedisCache
from app.domain.search.schemas import HybridSearchResponse, RetrievalContext
from app.services.search.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        retriever: HybridRetriever | None = None,
        cache: RedisCache | None = None,
        cache_ttl_seconds: int | None = None,
    ) -> None:
        self.retriever = retriever or HybridRetriever()
        self.cache = cache or RedisCache()
        self.cache_ttl_seconds = cache_ttl_seconds or settings.search_cache_ttl_seconds

    async def query(self, query: str, top_k: int) -> HybridSearchResponse:
        cache_key = self._cache_key(query, top_k)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return HybridSearchResponse.model_validate(cached)

        context = await self.retriever.retrieve(query=query, top_k=top_k)
        response = HybridSearchResponse(
            query=query,
            evidence=context.chunks,
            graph_context=context.graph_context,
            confidence_score=self._confidence_score(context),
        )
        await self.cache.set_json(cache_key, response.model_dump(mode="json"), self.cache_ttl_seconds)
        logger.info("hybrid_search_response_created", extra={"query_hash": cache_key, "evidence": len(response.evidence)})
        return response

    @staticmethod
    def _confidence_score(context: RetrievalContext) -> float:
        if not context.chunks:
            return 0.0
        evidence_score = sum(item.final_score for item in context.chunks) / len(context.chunks)
        graph_bonus = min(0.15, len(context.graph_context.related_nodes) / 100)
        return round(min(1.0, evidence_score * 0.85 + graph_bonus), 6)

    @staticmethod
    def _cache_key(query: str, top_k: int) -> str:
        digest = hashlib.sha256(f"{query.strip().lower()}|{top_k}".encode("utf-8")).hexdigest()
        return f"search:hybrid:{digest}"

