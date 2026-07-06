import asyncio
import json
import logging
import re

import google.generativeai as genai

from app.core.config import settings
from app.domain.chat.schemas import GeminiGroundedResponse

logger = logging.getLogger(__name__)


class GeminiClient:
    async def generate_grounded_answer(self, prompt: str) -> GeminiGroundedResponse:
        if not settings.gemini_api_key:
            logger.warning("gemini_api_key_missing_using_evidence_only_response")
            return GeminiGroundedResponse(
                answer=(
                    "I found relevant PlantMind evidence, but Gemini is not configured. "
                    "Set GEMINI_API_KEY to generate a grounded natural-language answer."
                ),
                confidence=0.35,
                cited_chunk_ids=[],
                follow_up_questions=[],
            )

        def run() -> str:
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
            )
            return response.text or "{}"

        raw = await asyncio.to_thread(run)
        try:
            return GeminiGroundedResponse.model_validate(json.loads(self._strip_json_fence(raw)))
        except Exception as exc:
            logger.exception("gemini_response_parse_failed")
            raise ValueError(f"Gemini returned an invalid grounded response: {exc}") from exc

    @staticmethod
    def _strip_json_fence(value: str) -> str:
        stripped = value.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
            stripped = re.sub(r"```$", "", stripped).strip()
        return stripped

