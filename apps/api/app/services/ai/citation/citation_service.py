from app.domain.chat.schemas import Citation, GeminiGroundedResponse
from app.domain.search.schemas import RetrievalContext


class CitationService:
    """Stub citation engine interface backed by retrieved evidence chunks."""

    async def resolve(self, model_response: GeminiGroundedResponse, context: RetrievalContext) -> list[Citation]:
        evidence_by_id = {item.chunk_id: item for item in context.chunks}
        requested_ids = model_response.cited_chunk_ids or [item.chunk_id for item in context.chunks[:3]]
        citations: list[Citation] = []

        for chunk_id in requested_ids:
            item = evidence_by_id.get(chunk_id)
            if item is None:
                continue
            metadata = getattr(item, "metadata", {})
            filename = metadata.get("filename") if isinstance(metadata, dict) else None
            citations.append(
                Citation(
                    document_id=item.document_id,
                    document=filename if isinstance(filename, str) else item.document_id,
                    chunk_id=item.chunk_id,
                    page_reference=item.page_reference,
                    page_number=self._page_number(item.page_reference),
                    quote=item.chunk_text[:300],
                    evidence=item.chunk_text[:500],
                    confidence=item.final_score,
                )
            )
        return citations

    @staticmethod
    def _page_number(page_reference: str | None) -> int | None:
        if not page_reference:
            return None
        digits = "".join(character for character in page_reference if character.isdigit())
        return int(digits) if digits else None
