import asyncio
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.agents.ingestion.agent import IngestionAgent
from app.core.config import settings
from app.db.mongodb.repositories import DocumentRepository
from app.domain.documents.exceptions import DocumentPipelineError, UnsupportedDocumentError
from app.domain.documents.schemas import DocumentListResponse, DocumentUploadResponse
from app.workflows.ingestion_workflow import create_initial_document_record

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def documents_health() -> dict[str, str]:
    return {"module": "documents", "status": "ready"}


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    repository = DocumentRepository()
    return DocumentListResponse(documents=await repository.list_documents())


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents(files: list[UploadFile] = File(...)) -> DocumentUploadResponse:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one PDF is required")

    agent = IngestionAgent()
    results = []

    for upload in files:
        try:
            pdf_bytes = await _read_pdf(upload)
            storage_path = await _store_upload(upload.filename or "document.pdf", pdf_bytes)
            document_id = await create_initial_document_record(
                filename=upload.filename or storage_path.name,
                content_type=upload.content_type or "application/pdf",
                file_size_bytes=len(pdf_bytes),
                storage_path=storage_path,
            )
            result = await agent.run(
                {
                    "document_id": document_id,
                    "filename": upload.filename or storage_path.name,
                    "file_path": str(storage_path),
                    "pdf_bytes": pdf_bytes,
                }
            )
            results.append(result)
        except UnsupportedDocumentError as exc:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)) from exc
        except DocumentPipelineError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("document_upload_failed", extra={"uploaded_file": upload.filename})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process {upload.filename}: {exc}",
            ) from exc

    return DocumentUploadResponse(documents=results)


async def _read_pdf(upload: UploadFile) -> bytes:
    filename = upload.filename or ""
    content_type = upload.content_type or ""
    if not filename.lower().endswith(".pdf") and content_type != "application/pdf":
        raise UnsupportedDocumentError(f"{filename or 'uploaded file'} is not a PDF")

    content = await upload.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise UnsupportedDocumentError(f"{filename} exceeds {settings.max_upload_mb} MB upload limit")
    if not content.startswith(b"%PDF"):
        raise UnsupportedDocumentError(f"{filename} does not appear to be a valid PDF")
    return content


async def _store_upload(filename: str, content: bytes) -> Path:
    storage_root = Path(settings.document_storage_root)
    await asyncio.to_thread(storage_root.mkdir, parents=True, exist_ok=True)
    safe_name = Path(filename).name
    storage_path = storage_root / f"{uuid4()}-{safe_name}"
    await asyncio.to_thread(storage_path.write_bytes, content)
    return storage_path
