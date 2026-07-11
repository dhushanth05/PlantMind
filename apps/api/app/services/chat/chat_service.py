import logging
from collections.abc import Iterable

from google.api_core.exceptions import GoogleAPIError, ResourceExhausted

from app.domain.chat.schemas import ChatRequest, ChatResponse, ConversationTurn, GeminiGroundedResponse
from app.services.ai.citation.citation_service import CitationService
from app.services.chat.conversation_memory import ConversationMemory
from app.services.chat.demo_answers import NO_EVIDENCE_FOLLOW_UPS, get_demo_answer
from app.services.chat.gemini_client import GeminiClient
from app.services.chat.prompt_builder import PromptBuilder
from app.services.chat.response_formatter import ResponseFormatter
from app.services.search.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        retriever: HybridRetriever | None = None,
        memory: ConversationMemory | None = None,
        prompt_builder: PromptBuilder | None = None,
        gemini_client: GeminiClient | None = None,
        citation_service: CitationService | None = None,
        formatter: ResponseFormatter | None = None,
    ) -> None:
        self.retriever = retriever or HybridRetriever()
        self.memory = memory or ConversationMemory()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.gemini_client = gemini_client or GeminiClient()
        self.citation_service = citation_service or CitationService()
        self.formatter = formatter or ResponseFormatter()

    async def respond(self, request: ChatRequest) -> ChatResponse:
        history = await self.memory.load(request.session_id)
        retrieval_context = await self.retriever.retrieve(query=request.message)
        if not retrieval_context.chunks:
            response = self._no_evidence_response()
            await self._store_turns(request.session_id, request.message, response.answer)
            return response

        prompt = self.prompt_builder.build(
            message=request.message,
            retrieval_context=retrieval_context,
            history=history,
        )
        try:
            model_response = await self.gemini_client.generate_grounded_answer(prompt)
        except (ResourceExhausted, GoogleAPIError, TimeoutError, ConnectionError) as exc:
            response = await self._fallback_response(request.message, retrieval_context, exc)
            await self._store_turns(request.session_id, request.message, response.answer)
            logger.warning(
                "chat_llm_failed_using_fallback",
                extra={"session_id": request.session_id, "error_type": type(exc).__name__},
            )
            return response
        except Exception as exc:
            response = await self._fallback_response(request.message, retrieval_context, exc)
            await self._store_turns(request.session_id, request.message, response.answer)
            logger.exception(
                "chat_unexpected_llm_failed_using_fallback",
                extra={"session_id": request.session_id, "error_type": type(exc).__name__},
            )
            return response

        citations = await self.citation_service.resolve(model_response, retrieval_context)
        response = self.formatter.format(
            model_response=model_response,
            retrieval_context=retrieval_context,
            citations=citations,
        )
        await self._store_turns(request.session_id, request.message, response.answer)
        logger.info(
            "chat_response_created",
            extra={
                "session_id": request.session_id,
                "citations": len(response.citations),
                "confidence": response.confidence,
            },
        )
        return response

    async def _fallback_response(self, message: str, retrieval_context, exc: Exception) -> ChatResponse:
        if self._is_quota_error(exc):
            demo_answer = get_demo_answer(message)
            if demo_answer is not None:
                return demo_answer

        if not retrieval_context.chunks:
            return self._no_evidence_response()

        cited_chunk_ids = [item.chunk_id for item in retrieval_context.chunks[:3]]
        citations = await self.citation_service.resolve(
            GeminiGroundedResponse(
                answer="",
                confidence=self._fallback_confidence(item.final_score for item in retrieval_context.chunks[:3]),
                cited_chunk_ids=cited_chunk_ids,
                related_assets=self._related_assets(retrieval_context),
                follow_up_questions=self._follow_up_questions(retrieval_context),
            ),
            retrieval_context,
        )
        return ChatResponse(
            answer=self._evidence_answer(retrieval_context.chunks[:4]),
            confidence=self._fallback_confidence(item.final_score for item in retrieval_context.chunks[:3]),
            citations=citations,
            related_assets=self._related_assets(retrieval_context),
            follow_up_questions=self._follow_up_questions(retrieval_context),
        )

    async def _store_turns(self, session_id: str, user_message: str, assistant_message: str) -> None:
        await self.memory.append(
            session_id,
            ConversationTurn(role="user", content=user_message),
            ConversationTurn(role="assistant", content=assistant_message),
        )

    @staticmethod
    def _no_evidence_response() -> ChatResponse:
        return ChatResponse(
            answer="No supporting evidence was found in the uploaded documents.",
            confidence=0.0,
            citations=[],
            related_assets=[],
            follow_up_questions=NO_EVIDENCE_FOLLOW_UPS,
        )

    @staticmethod
    def _is_quota_error(exc: Exception) -> bool:
        return isinstance(exc, ResourceExhausted) or "429" in str(exc) or "quota" in str(exc).lower()

    @staticmethod
    def _evidence_answer(chunks) -> str:
        bullets = []
        for chunk in chunks:
            sentence = chunk.chunk_text.replace("\n", " ").strip().split(".")[0].strip()
            if sentence:
                bullets.append(sentence[:220])
        if not bullets:
            return "No supporting evidence was found in the uploaded documents."
        lines = "\n".join(f"- {bullet}" for bullet in dict.fromkeys(bullets))
        return f"Based on retrieved PlantMind evidence:\n{lines}"

    @staticmethod
    def _fallback_confidence(scores: Iterable[float]) -> float:
        values = list(scores)
        if not values:
            return 0.0
        return round(min(0.85, max(0.35, sum(values) / len(values) * 0.76)), 6)

    @staticmethod
    def _related_assets(retrieval_context) -> list[str]:
        assets: list[str] = []
        for context in retrieval_context.asset_context:
            equipment_id = context.equipment.properties.get("equipment_id")
            name = context.equipment.properties.get("name")
            if isinstance(equipment_id, str):
                assets.append(equipment_id)
            if isinstance(name, str):
                assets.append(name)
        return list(dict.fromkeys(assets))[:10]

    @staticmethod
    def _follow_up_questions(retrieval_context) -> list[str]:
        questions: list[str] = []
        for context in retrieval_context.asset_context:
            equipment_id = context.equipment.properties.get("equipment_id")
            if isinstance(equipment_id, str):
                questions.extend(
                    [
                        f"What maintenance procedure applies to {equipment_id}?",
                        f"What inspections are required for {equipment_id}?",
                    ]
                )
        questions.append("Upload an incident report")
        return list(dict.fromkeys(questions))[:3]
