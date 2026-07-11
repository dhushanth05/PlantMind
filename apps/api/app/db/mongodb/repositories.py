from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from app.db.mongodb.client import mongo_database
from app.domain.documents.schemas import (
    DocumentChunk,
    DocumentRecord,
    DocumentSummary,
    EntityExtractionResult,
    GraphBuildResult,
    PDFExtractionResult,
)


class DocumentRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def create_document(self, document: DocumentRecord) -> str:
        result = await self.db.documents.insert_one(document.model_dump(mode="json"))
        return str(result.inserted_id)

    async def list_documents(self, limit: int = 50) -> list[DocumentSummary]:
        cursor = self.db.documents.find().sort("upload_timestamp", -1).limit(limit)
        documents = await cursor.to_list(length=limit)
        summaries: list[DocumentSummary] = []

        for document in documents:
            document_id = str(document.get("_id", ""))
            chunk_count = await self.db.chunks.count_documents({"document_id": document_id})
            entity_record = await self.db.document_entities.find_one({"document_id": document_id})
            entity_count = _count_entities(entity_record.get("entities", {}) if entity_record else {})
            upload_timestamp = _coerce_datetime(document.get("upload_timestamp"), fallback=datetime.now(UTC))
            processed_at = _coerce_datetime(document.get("processed_at"))
            failed_at = _coerce_datetime(document.get("failed_at"))
            finished_at = processed_at or failed_at

            summaries.append(
                DocumentSummary(
                    document_id=document_id,
                    filename=str(document.get("filename") or "Untitled document"),
                    content_type=str(document.get("content_type") or "application/pdf"),
                    file_size_bytes=int(document.get("file_size_bytes") or 0),
                    upload_timestamp=upload_timestamp,
                    status=str(document.get("status") or "uploaded"),
                    page_count=int(document["page_count"]) if document.get("page_count") is not None else None,
                    extraction_method=str(document["extraction_method"]) if document.get("extraction_method") is not None else None,
                    is_scanned=bool(document.get("is_scanned", False)),
                    processed_at=processed_at,
                    failed_at=failed_at,
                    error=str(document["error"]) if document.get("error") is not None else None,
                    extracted_entities=int(document.get("entities_found") or entity_count),
                    chunks_created=int(document.get("chunks_created") or chunk_count),
                    graph_nodes_created=int(document.get("graph_nodes_created") or 0),
                    graph_edges_created=int(document.get("graph_edges_created") or 0),
                    processing_duration_ms=_duration_ms(upload_timestamp, finished_at),
                )
            )

        return summaries

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

    async def mark_completed(
        self,
        document_id: str,
        *,
        chunks_created: int,
        entities_found: int,
        graph_result: GraphBuildResult,
    ) -> None:
        await self.db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "status": "completed",
                    "chunks_created": chunks_created,
                    "entities_found": entities_found,
                    "graph_nodes_created": graph_result.nodes_created,
                    "graph_edges_created": graph_result.edges_created,
                    "processed_at": datetime.now(UTC),
                },
                "$unset": {"error": "", "failed_at": ""},
            },
        )


def _count_entities(entities: dict[str, Any]) -> int:
    return sum(len(value) for value in entities.values() if isinstance(value, list))


def _coerce_datetime(value: Any, fallback: datetime | None = None) -> datetime | None:
    if value is None:
        return fallback
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return fallback
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return fallback


def _duration_ms(started_at: datetime | None, finished_at: datetime | None) -> int | None:
    if not started_at or not finished_at:
        return None
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    if finished_at.tzinfo is None:
        finished_at = finished_at.replace(tzinfo=UTC)
    return max(0, int((finished_at - started_at).total_seconds() * 1000))


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
