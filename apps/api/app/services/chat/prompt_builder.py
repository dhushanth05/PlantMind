import json

from app.domain.chat.schemas import ConversationTurn
from app.domain.search.schemas import RetrievalContext


class PromptBuilder:
    SYSTEM_PROMPT = """You are PlantMind, an industrial knowledge copilot.
Answer only from the retrieved context provided below.
Never invent facts, causes, document names, dates, procedures, or relationships.
If evidence is insufficient, say what is unknown and what evidence would be needed.
Summarize across multiple documents when multiple evidence chunks are relevant.
Explain relationships between equipment, incidents, procedures, personnel, and failure modes.
Keep the answer concise, technically accurate, and grounded.
Return strict JSON only with keys: answer, confidence, cited_chunk_ids, related_assets, follow_up_questions.
"""

    def build(self, message: str, retrieval_context: RetrievalContext, history: list[ConversationTurn]) -> str:
        payload = {
            "conversation_history": [
                {"role": turn.role, "content": turn.content, "created_at": turn.created_at.isoformat()}
                for turn in history
            ],
            "user_question": message,
            "retrieved_context": {
                "evidence_chunks": [
                    {
                        "chunk_id": item.chunk_id,
                        "document_id": item.document_id,
                        "page_reference": item.page_reference,
                        "text": item.chunk_text,
                        "final_score": item.final_score,
                    }
                    for item in retrieval_context.chunks
                ],
                "asset_context": [
                    {
                        "equipment": context.equipment.properties,
                        "incidents": [node.properties for node in context.connected_incidents],
                        "documents": [node.properties for node in context.connected_documents],
                        "personnel": [node.properties for node in context.connected_personnel],
                        "failure_modes": [node.properties for node in context.failure_modes],
                        "procedures": [node.properties for node in context.related_procedures],
                    }
                    for context in retrieval_context.asset_context
                ],
                "incidents": [node.properties for node in retrieval_context.incidents],
                "procedures": [node.properties for node in retrieval_context.procedures],
                "graph_relationships": [
                    {
                        "type": relationship.type,
                        "source": relationship.source,
                        "target": relationship.target,
                        "properties": relationship.properties,
                    }
                    for relationship in retrieval_context.graph_context.relationships[:50]
                ],
            },
            "response_requirements": {
                "citation_rule": "Only cite chunk IDs present in evidence_chunks.",
                "follow_up_questions": "Generate 2 or 3 next questions from the retrieved context.",
                "uncertainty": "Lower confidence and state uncertainty when context is thin or contradictory.",
            },
        }
        return f"{self.SYSTEM_PROMPT}\n\nCONTEXT_JSON:\n{json.dumps(payload, ensure_ascii=False)}"

