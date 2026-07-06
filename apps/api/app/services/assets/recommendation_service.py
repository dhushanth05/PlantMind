import asyncio
import json
import logging
import re

import google.generativeai as genai

from app.core.config import settings
from app.domain.assets.schemas import DigitalTwinRecommendation, RiskAssessment
from app.domain.graph.schemas import AssetContext
from app.domain.search.schemas import RetrievalContext

logger = logging.getLogger(__name__)


class RecommendationService:
    async def generate(
        self,
        asset_id: str,
        context: AssetContext,
        retrieval_context: RetrievalContext,
        risk: RiskAssessment,
    ) -> list[DigitalTwinRecommendation]:
        if settings.gemini_api_key:
            try:
                return await self._generate_with_gemini(asset_id, context, retrieval_context, risk)
            except Exception:
                logger.exception("digital_twin_recommendation_generation_failed", extra={"asset_id": asset_id})
        return self._rule_based(context, risk)

    async def _generate_with_gemini(
        self,
        asset_id: str,
        context: AssetContext,
        retrieval_context: RetrievalContext,
        risk: RiskAssessment,
    ) -> list[DigitalTwinRecommendation]:
        prompt = {
            "instruction": "Generate 3 concise industrial maintenance recommendations grounded only in this asset context. Return JSON array with title, rationale, priority.",
            "asset_id": asset_id,
            "risk": risk.model_dump(),
            "incidents": [node.properties for node in context.connected_incidents],
            "failure_modes": [node.properties for node in context.failure_modes],
            "procedures": [node.properties for node in context.related_procedures],
            "evidence": [item.model_dump() for item in retrieval_context.chunks[:5]],
        }

        def run() -> str:
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(
                json.dumps(prompt),
                generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
            )
            return response.text or "[]"

        raw = await asyncio.to_thread(run)
        data = json.loads(self._strip_json_fence(raw))
        return [DigitalTwinRecommendation.model_validate(item) for item in data][:3]

    @staticmethod
    def _rule_based(context: AssetContext, risk: RiskAssessment) -> list[DigitalTwinRecommendation]:
        recommendations: list[DigitalTwinRecommendation] = []
        if context.failure_modes:
            name = context.failure_modes[0].properties.get("name") or "recurring failure mode"
            recommendations.append(
                DigitalTwinRecommendation(
                    title=f"Inspect {name} within 7 days",
                    rationale="The asset has connected failure-mode evidence in the knowledge graph.",
                    priority=risk.level,
                )
            )
        if context.related_procedures:
            procedure = context.related_procedures[0].properties.get("name") or context.related_procedures[0].properties.get("procedure_id") or "linked SOP"
            recommendations.append(
                DigitalTwinRecommendation(
                    title=f"Review {procedure} before restart",
                    rationale="A related procedure is connected to the asset and should be verified against current condition.",
                    priority="Medium",
                )
            )
        recommendations.append(
            DigitalTwinRecommendation(
                title="Review recent incidents and maintenance evidence",
                rationale="Digital twin confidence improves when incident, inspection, and maintenance records are reconciled.",
                priority="Low" if risk.level == "Low" else "Medium",
            )
        )
        return recommendations[:3]

    @staticmethod
    def _strip_json_fence(value: str) -> str:
        stripped = value.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
            stripped = re.sub(r"```$", "", stripped).strip()
        return stripped

