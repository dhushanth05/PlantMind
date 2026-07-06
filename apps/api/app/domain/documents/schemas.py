from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


ExtractionMethod = Literal[
    "pdfplumber",
    "pypdf2",
    "gemini_vision_ocr",
    "pdfplumber_scanned_no_ocr_configured",
    "pypdf2_scanned_no_ocr_configured",
]


class PDFExtractionResult(BaseModel):
    document_text: str
    page_count: int
    extraction_method: ExtractionMethod
    page_texts: list[str] = Field(default_factory=list)
    is_scanned: bool = False


class DocumentRecord(BaseModel):
    filename: str
    content_type: str
    file_size_bytes: int
    storage_path: str
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "uploaded"
    page_count: int | None = None
    extraction_method: str | None = None


class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    page_reference: str
    chunk_text: str
    chunk_index: int


class EntityItem(BaseModel):
    id: str
    type: str | None = None
    name: str | None = None
    source: str = "pipeline"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EntityExtractionResult(BaseModel):
    equipment: list[EntityItem] = Field(default_factory=list)
    personnel: list[EntityItem] = Field(default_factory=list)
    procedures: list[EntityItem] = Field(default_factory=list)
    incidents: list[EntityItem] = Field(default_factory=list)
    failure_modes: list[EntityItem] = Field(default_factory=list)
    dates: list[EntityItem] = Field(default_factory=list)
    locations: list[EntityItem] = Field(default_factory=list)

    @property
    def total_count(self) -> int:
        return sum(len(value) for value in self.model_dump().values())


class GraphBuildResult(BaseModel):
    nodes_created: int = 0
    edges_created: int = 0


class DocumentUploadResult(BaseModel):
    document_id: str
    chunks_created: int
    entities_found: int
    graph_nodes_created: int
    graph_edges_created: int


class DocumentUploadResponse(BaseModel):
    documents: list[DocumentUploadResult]

