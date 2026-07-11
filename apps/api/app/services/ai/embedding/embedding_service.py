import asyncio
from datetime import UTC, datetime
from hashlib import blake2b
import logging
import math
from typing import Any

from app.core.config import settings
from app.domain.documents.schemas import DocumentChunk

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self._model: Any | None = None
        self._fallback = False

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ModuleNotFoundError:
                from app.services.ai.optional_ml import ensure_optional_ml_dependencies

                try:
                    ensure_optional_ml_dependencies()
                    from sentence_transformers import SentenceTransformer
                except Exception as exc:
                    logger.warning(
                        "sentence_transformers_unavailable_using_hash_embeddings",
                        extra={"error_type": type(exc).__name__},
                    )
                    self._fallback = True
                    return None

            self._model = SentenceTransformer(settings.sentence_transformer_model)
        return self._model

    async def embed_chunks(self, chunks: list[DocumentChunk]) -> list[dict[str, Any]]:
        if not chunks:
            return []

        model = self._load_model()
        if self._fallback or model is None:
            vectors = [self._hash_embedding(chunk.chunk_text) for chunk in chunks]
        else:
            vectors = await asyncio.to_thread(
                model.encode,
                [chunk.chunk_text for chunk in chunks],
                normalize_embeddings=True,
            )

        return [
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "model": self._model_name,
                "embedding": vector.tolist() if hasattr(vector, "tolist") else vector,
                "created_at": datetime.now(UTC),
            }
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

    async def embed_query(self, query: str) -> list[float]:
        model = self._load_model()
        if self._fallback or model is None:
            return self._hash_embedding(query)
        vector = await asyncio.to_thread(model.encode, query, normalize_embeddings=True)
        return vector.tolist()

    @property
    def _model_name(self) -> str:
        return "hash-fallback-384" if self._fallback else settings.sentence_transformer_model

    @staticmethod
    def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
        vector = [0.0] * dimensions
        tokens = text.lower().split()
        for token in tokens:
            digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
