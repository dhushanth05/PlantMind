import pytest

from app.domain.documents.exceptions import UnsupportedDocumentError
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
