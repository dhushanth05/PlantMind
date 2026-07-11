import logging
import re
from typing import Any

from app.core.config import settings
from app.db.mongodb.client import mongo_database
from app.domain.search.schemas import VectorSearchHit

logger = logging.getLogger(__name__)


class VectorSearchRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def search_chunks(self, query: str, query_embedding: list[float], top_k: int) -> list[VectorSearchHit]:
        pipeline: list[dict[str, Any]] = [
            {
                "$vectorSearch": {
                    "index": settings.mongodb_vector_index,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(top_k * 20, 50),
                    "limit": top_k,
                }
            },
            {
                "$lookup": {
                    "from": "chunks",
                    "localField": "chunk_id",
                    "foreignField": "chunk_id",
                    "as": "chunk",
                }
            },
            {"$unwind": "$chunk"},
            {
                "$project": {
                    "_id": 0,
                    "chunk_id": 1,
                    "document_id": 1,
                    "page_reference": "$chunk.page_reference",
                    "chunk_text": "$chunk.chunk_text",
                    "score": {"$meta": "vectorSearchScore"},
                    "metadata": {
                        "embedding_model": "$model",
                        "chunk_index": "$chunk.chunk_index",
                    },
                }
            },
        ]

        try:
            cursor = self.db.embeddings.aggregate(pipeline)
            return [VectorSearchHit.model_validate(document) async for document in cursor]
        except Exception:
            logger.exception("mongodb_vector_search_failed_using_text_fallback")
            return await self._text_search_chunks(query=query, top_k=top_k)

    async def _text_search_chunks(self, query: str, top_k: int) -> list[VectorSearchHit]:
        terms = [term for term in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}", query) if len(term) > 2]
        if not terms:
            return []

        pattern = "|".join(re.escape(term) for term in terms[:8])
        cursor = self.db.chunks.find({"chunk_text": {"$regex": pattern, "$options": "i"}}).limit(top_k)
        hits: list[VectorSearchHit] = []
        async for chunk in cursor:
            text = str(chunk.get("chunk_text", ""))
            score = self._text_score(text=text, terms=terms)
            hits.append(
                VectorSearchHit(
                    chunk_id=str(chunk.get("chunk_id", "")),
                    document_id=str(chunk.get("document_id", "")),
                    page_reference=str(chunk.get("page_reference", "")),
                    chunk_text=text,
                    score=score,
                    metadata={"retrieval": "text_fallback", "chunk_index": chunk.get("chunk_index")},
                )
            )
        hits.sort(key=lambda item: item.score, reverse=True)
        return hits

    @staticmethod
    def _text_score(text: str, terms: list[str]) -> float:
        normalized = text.lower()
        matches = sum(1 for term in terms if term.lower() in normalized)
        return round(min(1.0, matches / max(len(terms), 1)), 6)
