import logging
from typing import Any

from app.core.config import settings
from app.db.mongodb.client import mongo_database
from app.domain.search.schemas import VectorSearchHit

logger = logging.getLogger(__name__)


class VectorSearchRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def search_chunks(self, query_embedding: list[float], top_k: int) -> list[VectorSearchHit]:
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
            logger.exception("mongodb_vector_search_failed")
            raise

