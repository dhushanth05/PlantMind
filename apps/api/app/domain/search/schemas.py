from typing import Any

from pydantic import BaseModel, Field

from app.domain.documents.schemas import EntityExtractionResult
from app.domain.graph.schemas import AssetContext, GraphNode, GraphRelationship, GraphSubgraph


class SearchQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=25)


class VectorSearchHit(BaseModel):
    chunk_id: str
    document_id: str
    page_reference: str
    chunk_text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    chunk_id: str
    document_id: str
    page_reference: str
    chunk_text: str
    vector_score: float
    graph_relevance_score: float
    entity_overlap_score: float
    final_score: float


class HybridGraphContext(BaseModel):
    subgraphs: list[GraphSubgraph] = Field(default_factory=list)
    asset_contexts: list[AssetContext] = Field(default_factory=list)
    related_nodes: list[GraphNode] = Field(default_factory=list)
    relationships: list[GraphRelationship] = Field(default_factory=list)


class RetrievalContext(BaseModel):
    query: str
    chunks: list[EvidenceItem]
    graph_context: HybridGraphContext
    asset_context: list[AssetContext]
    incidents: list[GraphNode]
    procedures: list[GraphNode]


class HybridSearchResponse(BaseModel):
    query: str
    evidence: list[EvidenceItem]
    graph_context: HybridGraphContext
    confidence_score: float


class QueryAnalysis(BaseModel):
    query: str
    embedding: list[float]
    entities: EntityExtractionResult

