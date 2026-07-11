import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.domain.documents.exceptions import UnsupportedDocumentError
from app.db.mongodb.repositories import DocumentRepository
from app.api.v1.routes import documents as documents_route
from app.main import app
from app.services.ai.entity_extraction.entity_extraction_service import EntityExtractionService
from app.services.chunking_service import ChunkingService
from app.api.v1.routes.documents import _read_pdf


def test_chunking_service_creates_overlapping_chunks() -> None:
    text = "Pump P204 inspection finding. " * 100

    chunks = ChunkingService(chunk_size=1000, overlap=200).chunk_document(
        document_id="doc-1",
        document_text=text,
        page_texts=[text],
    )

    assert len(chunks) > 1
    assert all(chunk.document_id == "doc-1" for chunk in chunks)
    assert all(len(chunk.chunk_text) <= 1000 for chunk in chunks)
    assert chunks[0].page_reference == "page 1"


@pytest.mark.asyncio
async def test_entity_extraction_identifies_industrial_entities() -> None:
    text = "Pump P204 seal failure incident at Mumbai site. SOP-17 assigned to operator Ravi."

    entities = await EntityExtractionService().extract(text)

    assert any(item.id == "P204" and item.type == "Pump" for item in entities.equipment)
    assert any("SOP-17" in (item.name or "") for item in entities.procedures)
    assert any("incident" in (item.name or "").lower() for item in entities.incidents)


class FakeUpload:
    def __init__(self, filename: str, content_type: str, content: bytes) -> None:
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.mark.asyncio
async def test_read_pdf_rejects_non_pdf_content() -> None:
    upload = FakeUpload("notes.txt", "text/plain", b"not a pdf")

    with pytest.raises(UnsupportedDocumentError):
        await _read_pdf(upload)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_read_pdf_accepts_pdf_header() -> None:
    upload = FakeUpload("manual.pdf", "application/pdf", b"%PDF-1.7\n")

    content = await _read_pdf(upload)  # type: ignore[arg-type]

    assert content.startswith(b"%PDF")


class FakeCursor:
    def __init__(self, documents: list[dict]) -> None:
        self.documents = documents

    def sort(self, *_args):
        return self

    def limit(self, *_args):
        return self

    async def to_list(self, length: int):
        return self.documents[:length]


class FakeCollection:
    def __init__(self, documents: list[dict] | None = None, record: dict | None = None) -> None:
        self.documents = documents or []
        self.record = record

    def find(self):
        return FakeCursor(self.documents)

    async def count_documents(self, _query: dict) -> int:
        return 0

    async def find_one(self, _query: dict):
        return self.record


class FakeMongoDatabase:
    def __init__(self) -> None:
        self.documents = FakeCollection(
            [
                {
                    "_id": ObjectId("64f0f6f0f6f0f6f0f6f0f6f0"),
                    "filename": "pump-manual.pdf",
                    "content_type": "application/pdf",
                    "file_size_bytes": 2048,
                    "upload_timestamp": "2026-07-09T04:30:00Z",
                    "processed_at": "2026-07-09T04:30:02+00:00",
                    "status": "completed",
                    "graph_nodes_created": 3,
                    "graph_edges_created": 2,
                }
            ]
        )
        self.chunks = FakeCollection()
        self.document_entities = FakeCollection(record={"entities": {"equipment": [{"id": "P204"}], "incidents": []}})


def test_get_documents_serializes_mongo_records(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = DocumentRepository()
    repository.db = FakeMongoDatabase()  # type: ignore[assignment]
    monkeypatch.setattr(documents_route, "DocumentRepository", lambda: repository)

    client = TestClient(app)
    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "documents": [
            {
                "document_id": "64f0f6f0f6f0f6f0f6f0f6f0",
                "filename": "pump-manual.pdf",
                "content_type": "application/pdf",
                "file_size_bytes": 2048,
                "upload_timestamp": "2026-07-09T04:30:00Z",
                "status": "completed",
                "page_count": None,
                "extraction_method": None,
                "is_scanned": False,
                "processed_at": "2026-07-09T04:30:02Z",
                "failed_at": None,
                "error": None,
                "extracted_entities": 1,
                "chunks_created": 0,
                "graph_nodes_created": 3,
                "graph_edges_created": 2,
                "processing_duration_ms": 2000,
            }
        ]
    }
