import asyncio
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.domain.documents.schemas import DocumentChunk


class EmbeddingService:
    def __init__(self) -> None:
        self._model: Any | None = None

    def _load_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.sentence_transformer_model)
        return self._model

    async def embed_chunks(self, chunks: list[DocumentChunk]) -> list[dict[str, Any]]:
        if not chunks:
            return []

        model = self._load_model()
        vectors = await asyncio.to_thread(
            model.encode,
            [chunk.chunk_text for chunk in chunks],
            normalize_embeddings=True,
        )

        return [
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "model": settings.sentence_transformer_model,
                "embedding": vector.tolist(),
                "created_at": datetime.now(UTC),
            }
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

    async def embed_query(self, query: str) -> list[float]:
        model = self._load_model()
        vector = await asyncio.to_thread(model.encode, query, normalize_embeddings=True)
        return vector.tolist()
