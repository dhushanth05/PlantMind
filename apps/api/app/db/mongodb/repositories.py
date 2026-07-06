from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from app.db.mongodb.client import mongo_database
from app.domain.documents.schemas import DocumentChunk, DocumentRecord, EntityExtractionResult, PDFExtractionResult


class DocumentRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def create_document(self, document: DocumentRecord) -> str:
        result = await self.db.documents.insert_one(document.model_dump(mode="json"))
        return str(result.inserted_id)

    async def mark_processing(
        self,
        document_id: str,
        extraction: PDFExtractionResult,
    ) -> None:
        await self.db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "status": "processed",
                    "page_count": extraction.page_count,
                    "extraction_method": extraction.extraction_method,
                    "is_scanned": extraction.is_scanned,
                    "processed_at": datetime.now(UTC),
                }
            },
        )

    async def mark_failed(self, document_id: str, error: str) -> None:
        await self.db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"status": "failed", "error": error, "failed_at": datetime.now(UTC)}},
        )


class ChunkRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def insert_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0
        result = await self.db.chunks.insert_many([chunk.model_dump() for chunk in chunks])
        return len(result.inserted_ids)


class EmbeddingRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def insert_embeddings(self, embeddings: list[dict[str, Any]]) -> int:
        if not embeddings:
            return 0
        result = await self.db.embeddings.insert_many(embeddings)
        return len(result.inserted_ids)


class EntityRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def store_entities(self, document_id: str, entities: EntityExtractionResult) -> None:
        await self.db.document_entities.update_one(
            {"document_id": document_id},
            {
                "$set": {
                    "document_id": document_id,
                    "entities": entities.model_dump(),
                    "updated_at": datetime.now(UTC),
                }
            },
            upsert=True,
        )

    async def store_incidents(self, document_id: str, entities: EntityExtractionResult) -> int:
        if not entities.incidents:
            return 0
        result = await self.db.incidents.insert_many(
            [
                {
                    "document_id": document_id,
                    "incident_id": incident.id,
                    "name": incident.name,
                    "type": incident.type,
                    "metadata": incident.metadata,
                    "created_at": datetime.now(UTC),
                }
                for incident in entities.incidents
            ]
        )
        return len(result.inserted_ids)

