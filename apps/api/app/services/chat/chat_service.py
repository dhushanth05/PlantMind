import logging

from app.domain.chat.schemas import ChatRequest, ChatResponse, ConversationTurn
from app.services.ai.citation.citation_service import CitationService
from app.services.chat.conversation_memory import ConversationMemory
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
        prompt = self.prompt_builder.build(
            message=request.message,
            retrieval_context=retrieval_context,
            history=history,
        )
        model_response = await self.gemini_client.generate_grounded_answer(prompt)
        citations = await self.citation_service.resolve(model_response, retrieval_context)
        response = self.formatter.format(
            model_response=model_response,
            retrieval_context=retrieval_context,
            citations=citations,
        )
        await self.memory.append(
            request.session_id,
            ConversationTurn(role="user", content=request.message),
            ConversationTurn(role="assistant", content=response.answer),
        )
        logger.info(
            "chat_response_created",
            extra={
                "session_id": request.session_id,
                "citations": len(response.citations),
                "confidence": response.confidence,
            },
        )
        return response

