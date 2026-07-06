import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.search import get_search_service
from app.domain.graph.schemas import AssetContext, GraphNode, GraphRelationship
from app.domain.search.schemas import HybridGraphContext, RetrievalContext, VectorSearchHit
from app.main import app
from app.services.search.ranking_service import RankingService
from app.services.search.search_service import SearchService


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[str, dict | list] = {}

    async def get_json(self, key: str):
        return self.values.get(key)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        self.values[key] = value


class FakeRetriever:
    def __init__(self) -> None:
        self.calls = 0

    async def retrieve(self, query: str, top_k: int) -> RetrievalContext:
        self.calls += 1
        equipment = GraphNode(id="eq-1", labels=["Equipment"], properties={"equipment_id": "P204", "name": "Pump P204"})
        document = GraphNode(id="doc-1", labels=["Document"], properties={"document_id": "doc-a"})
        incident = GraphNode(id="inc-1", labels=["Incident"], properties={"name": "Seal failure incident"})
        procedure = GraphNode(id="proc-1", labels=["Procedure"], properties={"name": "SOP-17"})
        relationship = GraphRelationship(id="rel-1", type="MENTIONED_IN", source="eq-1", target="doc-1")
        graph_context = HybridGraphContext(
            asset_contexts=[
                AssetContext(
                    equipment=equipment,
                    connected_incidents=[incident],
                    connected_documents=[document],
                    connected_personnel=[],
                    failure_modes=[],
                    related_procedures=[procedure],
                    relationships=[relationship],
                )
            ],
            related_nodes=[equipment, document, incident, procedure],
            relationships=[relationship],
        )
        evidence = RankingService().rank(
            hits=[
                VectorSearchHit(
                    chunk_id="chunk-1",
                    document_id="doc-a",
                    page_reference="page 4",
                    chunk_text="Pump P204 seal failure repeated after SOP-17 maintenance.",
                    score=0.8,
                )
            ],
            entities=await _query_entities(),
            graph_context=graph_context,
            top_k=top_k,
        )
        return RetrievalContext(
            query=query,
            chunks=evidence,
            graph_context=graph_context,
            asset_context=graph_context.asset_contexts,
            incidents=[incident],
            procedures=[procedure],
        )


async def _query_entities():
    from app.domain.documents.schemas import EntityExtractionResult, EntityItem

    return EntityExtractionResult(
        equipment=[EntityItem(id="P204", name="P204", type="Pump")],
        procedures=[EntityItem(id="SOP-17", name="SOP-17", type="Procedure")],
    )


@pytest.mark.asyncio
async def test_search_service_caches_response() -> None:
    retriever = FakeRetriever()
    service = SearchService(retriever=retriever, cache=FakeCache(), cache_ttl_seconds=30)

    first = await service.query("Why is Pump P204 failing repeatedly?", top_k=5)
    second = await service.query("Why is Pump P204 failing repeatedly?", top_k=5)

    assert first.evidence[0].document_id == "doc-a"
    assert second.confidence_score > 0
    assert retriever.calls == 1


def test_ranking_boosts_graph_and_entity_overlap() -> None:
    equipment = GraphNode(id="eq-1", labels=["Equipment"], properties={"equipment_id": "P204"})
    document = GraphNode(id="doc-1", labels=["Document"], properties={"document_id": "doc-a"})
    graph_context = HybridGraphContext(
        related_nodes=[equipment, document],
        asset_contexts=[
            AssetContext(
                equipment=equipment,
                connected_incidents=[],
                connected_documents=[document],
                connected_personnel=[],
                failure_modes=[],
                related_procedures=[],
                relationships=[],
            )
        ],
    )

    from app.domain.documents.schemas import EntityExtractionResult, EntityItem

    result = RankingService().rank(
        hits=[
            VectorSearchHit(
                chunk_id="chunk-a",
                document_id="doc-a",
                page_reference="page 1",
                chunk_text="Pump P204 repeated seal failure.",
                score=0.7,
            ),
            VectorSearchHit(
                chunk_id="chunk-b",
                document_id="doc-b",
                page_reference="page 2",
                chunk_text="Unrelated compressor note.",
                score=0.72,
            ),
        ],
        entities=EntityExtractionResult(equipment=[EntityItem(id="P204", name="Pump P204", type="Pump")]),
        graph_context=graph_context,
        top_k=2,
    )

    assert result[0].chunk_id == "chunk-a"
    assert result[0].graph_relevance_score == 1.0


def test_search_route_returns_hybrid_response() -> None:
    service = SearchService(retriever=FakeRetriever(), cache=FakeCache(), cache_ttl_seconds=30)
    app.dependency_overrides[get_search_service] = lambda: service
    try:
        client = TestClient(app)

        response = client.post("/api/v1/search/query", json={"query": "Why is Pump P204 failing repeatedly?"})

        assert response.status_code == 200
        payload = response.json()
        assert payload["query"] == "Why is Pump P204 failing repeatedly?"
        assert payload["evidence"][0]["chunk_id"] == "chunk-1"
        assert payload["graph_context"]["asset_contexts"][0]["equipment"]["properties"]["equipment_id"] == "P204"
    finally:
        app.dependency_overrides.clear()
