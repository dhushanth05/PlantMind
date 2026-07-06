from app.domain.chat.schemas import ChatResponse, Citation, GeminiGroundedResponse
from app.domain.search.schemas import RetrievalContext


class ResponseFormatter:
    def format(
        self,
        model_response: GeminiGroundedResponse,
        retrieval_context: RetrievalContext,
        citations: list[Citation],
    ) -> ChatResponse:
        related_assets = self._related_assets(model_response, retrieval_context)
        follow_ups = self._follow_up_questions(model_response, retrieval_context)
        confidence = self._confidence(model_response.confidence, retrieval_context)
        return ChatResponse(
            answer=model_response.answer.strip(),
            confidence=confidence,
            citations=citations,
            related_assets=related_assets,
            follow_up_questions=follow_ups,
        )

    @staticmethod
    def _related_assets(model_response: GeminiGroundedResponse, retrieval_context: RetrievalContext) -> list[str]:
        assets = list(model_response.related_assets)
        for context in retrieval_context.asset_context:
            equipment_id = context.equipment.properties.get("equipment_id")
            name = context.equipment.properties.get("name")
            if isinstance(equipment_id, str):
                assets.append(equipment_id)
            if isinstance(name, str):
                assets.append(name)
        return list(dict.fromkeys(assets))[:10]

    @staticmethod
    def _follow_up_questions(
        model_response: GeminiGroundedResponse,
        retrieval_context: RetrievalContext,
    ) -> list[str]:
        questions = [question for question in model_response.follow_up_questions if question.strip()]
        for context in retrieval_context.asset_context:
            equipment_id = context.equipment.properties.get("equipment_id")
            if isinstance(equipment_id, str):
                questions.append(f"What maintenance procedure applies to {equipment_id}?")
                questions.append(f"Show previous incidents involving {equipment_id}.")
            for failure_mode in context.failure_modes:
                name = failure_mode.properties.get("name")
                if isinstance(name, str):
                    questions.append(f"Show previous incidents involving {name}.")
        return list(dict.fromkeys(questions))[:3]

    @staticmethod
    def _confidence(model_confidence: float, retrieval_context: RetrievalContext) -> float:
        if not retrieval_context.chunks:
            return 0.0
        retrieval_score = sum(item.final_score for item in retrieval_context.chunks) / len(retrieval_context.chunks)
        return round(min(1.0, model_confidence * 0.7 + retrieval_score * 0.3), 6)

