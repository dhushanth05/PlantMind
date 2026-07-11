import logging
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.db.mongodb.repositories import ChunkRepository, DocumentRepository, EmbeddingRepository, EntityRepository
from app.db.neo4j.graph_service import KnowledgeGraphService
from app.db.redis.cache import RedisCache
from app.domain.documents.exceptions import DocumentPipelineError
from app.domain.documents.schemas import (
    DocumentChunk,
    DocumentRecord,
    DocumentUploadResult,
    EntityExtractionResult,
    GraphBuildResult,
    PDFExtractionResult,
)
from app.services.ai.embedding.embedding_service import EmbeddingService
from app.services.ai.entity_extraction.entity_extraction_service import EntityExtractionService
from app.services.chunking_service import ChunkingService
from app.services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class IngestionWorkflowInput(TypedDict):
    document_id: str
    filename: str
    file_path: str
    pdf_bytes: bytes


class IngestionState(TypedDict, total=False):
    document_id: str
    filename: str
    file_path: str
    pdf_bytes: bytes
    extraction: PDFExtractionResult
    chunks: list[DocumentChunk]
    entities: EntityExtractionResult
    graph_result: GraphBuildResult
    embeddings: list[dict]
    response: DocumentUploadResult


class IngestionWorkflow:
    def __init__(self) -> None:
        self.pdf_processor = PDFProcessor()
        self.chunking_service = ChunkingService(chunk_size=1000, overlap=200)
        self.entity_service = EntityExtractionService()
        self.embedding_service = EmbeddingService()
        self.document_repository = DocumentRepository()
        self.chunk_repository = ChunkRepository()
        self.entity_repository = EntityRepository()
        self.embedding_repository = EmbeddingRepository()
        self.graph_service = KnowledgeGraphService()
        self.cache = RedisCache()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(IngestionState)
        workflow.add_node("upload", self._upload)
        workflow.add_node("extract", self._extract)
        workflow.add_node("chunk", self._chunk)
        workflow.add_node("extract_entities", self._entities)
        workflow.add_node("graph_build", self._graph_build)
        workflow.add_node("generate_embeddings", self._embeddings)
        workflow.add_node("persist", self._persist)

        workflow.set_entry_point("upload")
        workflow.add_edge("upload", "extract")
        workflow.add_edge("extract", "chunk")
        workflow.add_edge("chunk", "extract_entities")
        workflow.add_edge("extract_entities", "graph_build")
        workflow.add_edge("graph_build", "generate_embeddings")
        workflow.add_edge("generate_embeddings", "persist")
        workflow.add_edge("persist", END)
        return workflow.compile()

    async def run(self, workflow_input: IngestionWorkflowInput) -> DocumentUploadResult:
        document_id = workflow_input["document_id"]
        try:
            state = await self.graph.ainvoke(workflow_input)
            return state["response"]
        except Exception as exc:
            await self.document_repository.mark_failed(document_id, str(exc))
            logger.exception("document_ingestion_failed", extra={"document_id": document_id})
            raise

    async def _upload(self, state: IngestionState) -> IngestionState:
        file_path = Path(state["file_path"])
        if not file_path.exists():
            raise DocumentPipelineError(f"Uploaded file is missing from storage: {file_path}")
        logger.info(
            "document_upload_registered",
            extra={
                "document_id": state["document_id"],
                "uploaded_file": state["filename"],
                "file_path": str(file_path),
            },
        )
        return {}

    async def _extract(self, state: IngestionState) -> IngestionState:
        extraction = await self.pdf_processor.process(state["pdf_bytes"], state["filename"])
        await self.document_repository.mark_processing(state["document_id"], extraction)
        logger.info(
            "document_extracted",
            extra={
                "document_id": state["document_id"],
                "method": extraction.extraction_method,
                "pages": extraction.page_count,
            },
        )
        return {"extraction": extraction}

    async def _chunk(self, state: IngestionState) -> IngestionState:
        extraction = state["extraction"]
        chunks = self.chunking_service.chunk_document(
            document_id=state["document_id"],
            document_text=extraction.document_text,
            page_texts=extraction.page_texts,
        )
        logger.info("document_chunked", extra={"document_id": state["document_id"], "chunks": len(chunks)})
        return {"chunks": chunks}

    async def _entities(self, state: IngestionState) -> IngestionState:
        entities = await self.entity_service.extract(state["extraction"].document_text)
        logger.info(
            "entities_extracted",
            extra={"document_id": state["document_id"], "entities": entities.total_count},
        )
        return {"entities": entities}

    async def _graph_build(self, state: IngestionState) -> IngestionState:
        graph_result = await self.graph_service.build_document_graph(
            document_id=state["document_id"],
            filename=state["filename"],
            entities=state["entities"],
        )
        return {"graph_result": graph_result}

    async def _embeddings(self, state: IngestionState) -> IngestionState:
        embeddings = await self.embedding_service.embed_chunks(state["chunks"])
        logger.info("embeddings_generated", extra={"document_id": state["document_id"], "count": len(embeddings)})
        return {"embeddings": embeddings}

    async def _persist(self, state: IngestionState) -> IngestionState:
        await self.chunk_repository.insert_chunks(state["chunks"])
        await self.entity_repository.store_entities(state["document_id"], state["entities"])
        await self.entity_repository.store_incidents(state["document_id"], state["entities"])
        await self.embedding_repository.insert_embeddings(state["embeddings"])
        await self.cache.delete_pattern("digital_twin:*")

        graph_result = state["graph_result"]
        await self.document_repository.mark_completed(
            state["document_id"],
            chunks_created=len(state["chunks"]),
            entities_found=state["entities"].total_count,
            graph_result=graph_result,
        )
        response = DocumentUploadResult(
            document_id=state["document_id"],
            chunks_created=len(state["chunks"]),
            entities_found=state["entities"].total_count,
            graph_nodes_created=graph_result.nodes_created,
            graph_edges_created=graph_result.edges_created,
        )
        logger.info("document_ingestion_complete", extra=response.model_dump())
        return {"response": response}


async def create_initial_document_record(
    *,
    filename: str,
    content_type: str,
    file_size_bytes: int,
    storage_path: Path,
) -> str:
    repository = DocumentRepository()
    return await repository.create_document(
        DocumentRecord(
            filename=filename,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            storage_path=str(storage_path),
        )
    )
