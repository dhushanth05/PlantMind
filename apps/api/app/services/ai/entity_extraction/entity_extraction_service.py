import asyncio
import json
import logging
import re
from hashlib import sha1
from typing import Any

import google.generativeai as genai

from app.core.config import settings
from app.domain.documents.schemas import EntityExtractionResult, EntityItem

logger = logging.getLogger(__name__)


class EntityExtractionService:
    def __init__(self) -> None:
        self._nlp: Any | None = None

    async def extract(self, text: str) -> EntityExtractionResult:
        spacy_entities = await asyncio.to_thread(self._extract_with_spacy, text)
        industrial_entities = self._extract_industrial_patterns(text)
        gemini_entities = await self._extract_with_gemini(text) if settings.gemini_api_key else EntityExtractionResult()
        return self._merge_results(spacy_entities, industrial_entities, gemini_entities)

    def _load_spacy(self) -> Any:
        if self._nlp is not None:
            return self._nlp
        try:
            import spacy
        except ModuleNotFoundError:
            from app.services.ai.optional_ml import ensure_optional_ml_dependencies

            try:
                ensure_optional_ml_dependencies()
                import spacy
            except Exception as exc:
                logger.warning(
                    "spacy_unavailable_using_pattern_entities_only",
                    extra={"error_type": type(exc).__name__},
                )
                return None

        try:
            self._nlp = spacy.load(settings.spacy_model)
        except OSError:
            logger.warning("spacy_model_not_found_using_blank_model", extra={"model": settings.spacy_model})
            self._nlp = spacy.blank("en")
            self._nlp.add_pipe("sentencizer")
        return self._nlp

    def _extract_with_spacy(self, text: str) -> EntityExtractionResult:
        nlp = self._load_spacy()
        if nlp is None:
            return EntityExtractionResult()
        doc = nlp(text[:1_000_000])
        result = EntityExtractionResult()
        for entity in doc.ents:
            item = EntityItem(
                id=self._stable_id(entity.text),
                name=entity.text,
                type=entity.label_,
                source="spacy",
            )
            if entity.label_ in {"PERSON"}:
                result.personnel.append(item)
            elif entity.label_ in {"DATE", "TIME"}:
                result.dates.append(item)
            elif entity.label_ in {"GPE", "LOC", "FAC"}:
                result.locations.append(item)
        return result

    def _extract_industrial_patterns(self, text: str) -> EntityExtractionResult:
        result = EntityExtractionResult()

        equipment_pattern = re.compile(
            r"\b(?:(pump|compressor|valve|motor|turbine|boiler|tank|vessel|conveyor|reactor|line|pipe)\s+)?([A-Z]{1,5}[- ]?\d{2,5}[A-Z]?)\b",
            re.IGNORECASE,
        )
        for match in equipment_pattern.finditer(text):
            equipment_type = (match.group(1) or "Equipment").title()
            equipment_id = match.group(2).replace(" ", "-").upper()
            if equipment_id.startswith(("SOP", "WI", "LOTO")):
                continue
            result.equipment.append(
                EntityItem(id=equipment_id, name=equipment_id, type=equipment_type, source="pattern")
            )

        procedure_pattern = re.compile(
            r"\b(SOP|procedure|work instruction|permit|lockout|tagout|LOTO|maintenance plan|inspection checklist)\b[^.\n]{0,120}",
            re.IGNORECASE,
        )
        for match in procedure_pattern.finditer(text):
            value = match.group(0).strip()
            result.procedures.append(
                EntityItem(id=self._stable_id(value), name=value, type="Procedure", source="pattern")
            )

        incident_pattern = re.compile(
            r"\b(incident|near miss|failure|shutdown|trip|leak|fire|explosion|release|spill|injury)\b[^.\n]{0,160}",
            re.IGNORECASE,
        )
        for match in incident_pattern.finditer(text):
            value = match.group(0).strip()
            result.incidents.append(
                EntityItem(id=self._stable_id(value), name=value, type="Incident", source="pattern")
            )

        failure_pattern = re.compile(
            r"\b(corrosion|fatigue|overpressure|overheating|vibration|seal failure|bearing failure|cavitation|blockage|rupture|short circuit)\b",
            re.IGNORECASE,
        )
        for match in failure_pattern.finditer(text):
            value = match.group(0).strip()
            result.failure_modes.append(
                EntityItem(id=self._stable_id(value), name=value, type="Failure Mode", source="pattern")
            )

        return result

    async def _extract_with_gemini(self, text: str) -> EntityExtractionResult:
        prompt = """
Extract industrial entities from the text as strict JSON with keys:
equipment, personnel, procedures, incidents, failure_modes, dates, locations.
Each item must contain id, type, and name. Return JSON only.
"""

        def run() -> str:
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(
                [prompt, text[:120_000]],
                generation_config={"temperature": 0, "response_mime_type": "application/json"},
            )
            return response.text or "{}"

        try:
            raw = await asyncio.to_thread(run)
            data = json.loads(self._strip_json_fence(raw))
            return self._result_from_mapping(data, source="gemini")
        except Exception:
            logger.exception("gemini_entity_extraction_failed")
            return EntityExtractionResult()

    def _result_from_mapping(self, data: dict[str, Any], source: str) -> EntityExtractionResult:
        fields = {}
        for key in EntityExtractionResult.model_fields:
            fields[key] = [
                EntityItem(
                    id=str(item.get("id") or self._stable_id(str(item))),
                    type=item.get("type"),
                    name=item.get("name") or item.get("id"),
                    source=source,
                    metadata={k: v for k, v in item.items() if k not in {"id", "type", "name"}},
                )
                for item in data.get(key, [])
                if isinstance(item, dict)
            ]
        return EntityExtractionResult(**fields)

    def _merge_results(self, *results: EntityExtractionResult) -> EntityExtractionResult:
        merged: dict[str, list[EntityItem]] = {key: [] for key in EntityExtractionResult.model_fields}
        seen: set[tuple[str, str]] = set()
        for result in results:
            for key in EntityExtractionResult.model_fields:
                for item in getattr(result, key):
                    identity = (key, item.id.lower())
                    if identity in seen:
                        continue
                    seen.add(identity)
                    merged[key].append(item)
        return EntityExtractionResult(**merged)

    @staticmethod
    def _stable_id(value: str) -> str:
        normalized = re.sub(r"\s+", " ", value.strip())
        return sha1(normalized.lower().encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _strip_json_fence(value: str) -> str:
        stripped = value.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
            stripped = re.sub(r"```$", "", stripped).strip()
        return stripped
