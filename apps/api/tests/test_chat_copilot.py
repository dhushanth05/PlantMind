import json
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.chat import get_chat_service
from app.domain.chat.schemas import ChatRequest, ConversationTurn, GeminiGroundedResponse
from app.domain.graph.schemas import AssetContext, GraphNode, GraphRelationship
from app.domain.search.schemas import EvidenceItem, HybridGraphContext, RetrievalContext
from app.main import app
from app.services.ai.citation.citation_service import CitationService
from app.services.chat.chat_service import ChatService
from app.services.chat.prompt_builder import PromptBuilder
from app.services.chat.response_formatter import ResponseFormatter


class FakeRetriever:
    async def retrieve(self, query: str, top_k: int | None = None) -> RetrievalContext:
        equipment = GraphNode(id="eq-1", labels=["Equipment"], properties={"equipment_id": "P204", "name": "Pump P204"})
        document = GraphNode(id="doc-1", labels=["Document"], properties={"document_id": "doc-a"})
        incident = GraphNode(id="inc-1", labels=["Incident"], properties={"name": "Seal leakage incident"})
        procedure = GraphNode(id="proc-1", labels=["Procedure"], properties={"name": "SOP-17"})
        failure_mode = GraphNode(id="fm-1", labels=["FailureMode"], properties={"name": "Seal Leakage"})
        relationship = GraphRelationship(id="rel-1", type="CAUSED_BY", source="inc-1", target="eq-1")
        asset_context = AssetContext(
            equipment=equipment,
            connected_incidents=[incident],
            connected_documents=[document],
            connected_personnel=[],
            failure_modes=[failure_mode],
            related_procedures=[procedure],
            relationships=[relationship],
        )
        graph_context = HybridGraphContext(
            asset_contexts=[asset_context],
            related_nodes=[equipment, document, incident, procedure, failure_mode],
            relationships=[relationship],
        )
        evidence = [
            EvidenceItem(
                chunk_id="chunk-1",
                document_id="doc-a",
                page_reference="page 4",
                chunk_text="Pump P204 has repeated seal leakage after maintenance.",
                vector_score=0.8,
                graph_relevance_score=1.0,
                entity_overlap_score=0.5,
                final_score=0.83,
            )
        ]
        return RetrievalContext(
            query=query,
            chunks=evidence,
            graph_context=graph_context,
            asset_context=[asset_context],
            incidents=[incident],
            procedures=[procedure],
        )


class FakeMemory:
    def __init__(self) -> None:
        self.turns: list[ConversationTurn] = []

    async def load(self, session_id: str) -> list[ConversationTurn]:
        return self.turns

    async def append(self, session_id: str, *turns: ConversationTurn) -> None:
        self.turns.extend(turns)


class FakeGemini:
    async def generate_grounded_answer(self, prompt: str) -> GeminiGroundedResponse:
        assert "CONTEXT_JSON" in prompt
        return GeminiGroundedResponse(
            answer="Pump P204 is repeatedly failing due to seal leakage evidenced after maintenance.",
            confidence=0.9,
            cited_chunk_ids=["chunk-1"],
            related_assets=["P204"],
            follow_up_questions=["What maintenance procedure applies to Pump P204?"],
        )


@pytest.mark.asyncio
async def test_chat_service_grounds_answer_and_stores_memory() -> None:
    memory = FakeMemory()
    service = ChatService(retriever=FakeRetriever(), memory=memory, gemini_client=FakeGemini())

    response = await service.respond(ChatRequest(session_id="s1", message="Why is Pump P204 failing repeatedly?"))

    assert "Pump P204" in response.answer
    assert response.confidence > 0.85
    assert response.citations[0].chunk_id == "chunk-1"
    assert "P204" in response.related_assets
    assert len(memory.turns) == 2


@pytest.mark.asyncio
async def test_citation_service_falls_back_to_top_evidence() -> None:
    context = await FakeRetriever().retrieve("Why is Pump P204 failing repeatedly?")

    citations = await CitationService().resolve(
        GeminiGroundedResponse(answer="Grounded answer", confidence=0.7),
        context,
    )

    assert citations[0].document_id == "doc-a"
    assert citations[0].quote is not None


def test_prompt_builder_contains_grounding_rules_and_context() -> None:
    context = asyncio.run(FakeRetriever().retrieve("Why is Pump P204 failing repeatedly?"))

    prompt = PromptBuilder().build(
        message="Why is Pump P204 failing repeatedly?",
        retrieval_context=context,
        history=[ConversationTurn(role="user", content="Earlier question")],
    )

    assert "Never invent facts" in prompt
    assert "Pump P204" in prompt
    assert "chunk-1" in prompt
    payload = json.loads(prompt.split("CONTEXT_JSON:\n", 1)[1])
    assert payload["retrieved_context"]["evidence_chunks"][0]["chunk_id"] == "chunk-1"


def test_response_formatter_generates_follow_ups_from_context() -> None:
    context = asyncio.run(FakeRetriever().retrieve("Why is Pump P204 failing repeatedly?"))

    response = ResponseFormatter().format(
        model_response=GeminiGroundedResponse(answer="Answer", confidence=0.8),
        retrieval_context=context,
        citations=[],
    )

    assert "What maintenance procedure applies to P204?" in response.follow_up_questions
    assert "P204" in response.related_assets


def test_chat_route_returns_copilot_response() -> None:
    service = ChatService(retriever=FakeRetriever(), memory=FakeMemory(), gemini_client=FakeGemini())
    app.dependency_overrides[get_chat_service] = lambda: service
    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/chat",
            json={"session_id": "s1", "message": "Why is Pump P204 failing repeatedly?"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["citations"][0]["chunk_id"] == "chunk-1"
        assert payload["follow_up_questions"]
    finally:
        app.dependency_overrides.clear()
