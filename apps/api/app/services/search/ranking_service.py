import re

from app.domain.documents.schemas import EntityExtractionResult
from app.domain.graph.schemas import AssetContext, GraphNode
from app.domain.search.schemas import EvidenceItem, HybridGraphContext, VectorSearchHit


class RankingService:
    def rank(
        self,
        hits: list[VectorSearchHit],
        entities: EntityExtractionResult,
        graph_context: HybridGraphContext,
        top_k: int,
    ) -> list[EvidenceItem]:
        graph_document_ids = self._graph_document_ids(graph_context)
        entity_terms = self._entity_terms(entities, graph_context.asset_contexts)
        ranked = [
            self._score_hit(hit=hit, graph_document_ids=graph_document_ids, entity_terms=entity_terms)
            for hit in hits
        ]
        ranked.sort(key=lambda item: item.final_score, reverse=True)
        return ranked[:top_k]

    def _score_hit(
        self,
        hit: VectorSearchHit,
        graph_document_ids: set[str],
        entity_terms: set[str],
    ) -> EvidenceItem:
        graph_relevance = 1.0 if hit.document_id in graph_document_ids else 0.0
        entity_overlap = self._entity_overlap_score(hit.chunk_text, entity_terms)
        final_score = min(1.0, hit.score * 0.6 + graph_relevance * 0.25 + entity_overlap * 0.15)
        return EvidenceItem(
            chunk_id=hit.chunk_id,
            document_id=hit.document_id,
            page_reference=hit.page_reference,
            chunk_text=hit.chunk_text,
            vector_score=round(hit.score, 6),
            graph_relevance_score=round(graph_relevance, 6),
            entity_overlap_score=round(entity_overlap, 6),
            final_score=round(final_score, 6),
        )

    @staticmethod
    def _entity_terms(entities: EntityExtractionResult, asset_contexts: list[AssetContext]) -> set[str]:
        terms: set[str] = set()
        for collection in [
            entities.equipment,
            entities.personnel,
            entities.procedures,
            entities.incidents,
            entities.failure_modes,
        ]:
            for item in collection:
                terms.add(item.id.lower())
                if item.name:
                    terms.add(item.name.lower())

        for context in asset_contexts:
            for node in [
                context.equipment,
                *context.connected_incidents,
                *context.connected_personnel,
                *context.failure_modes,
                *context.related_procedures,
            ]:
                terms.update(RankingService._node_terms(node))
        return {term for term in terms if term}

    @staticmethod
    def _node_terms(node: GraphNode) -> set[str]:
        values = [str(value).lower() for value in node.properties.values() if isinstance(value, str)]
        return set(values)

    @staticmethod
    def _graph_document_ids(graph_context: HybridGraphContext) -> set[str]:
        document_ids: set[str] = set()
        for context in graph_context.asset_contexts:
            for document in context.connected_documents:
                document_id = document.properties.get("document_id")
                if isinstance(document_id, str):
                    document_ids.add(document_id)
        for node in graph_context.related_nodes:
            if "Document" in node.labels:
                document_id = node.properties.get("document_id")
                if isinstance(document_id, str):
                    document_ids.add(document_id)
        return document_ids

    @staticmethod
    def _entity_overlap_score(text: str, entity_terms: set[str]) -> float:
        if not entity_terms:
            return 0.0
        normalized = re.sub(r"\s+", " ", text.lower())
        matches = sum(1 for term in entity_terms if term in normalized)
        return min(1.0, matches / max(len(entity_terms), 1))

