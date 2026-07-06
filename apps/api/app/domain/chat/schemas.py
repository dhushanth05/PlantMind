from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=4000)


class Citation(BaseModel):
    document_id: str
    document: str | None = None
    chunk_id: str | None = None
    page_reference: str | None = None
    page_number: int | None = None
    quote: str | None = None
    evidence: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
    related_assets: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


class ConversationTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GeminiGroundedResponse(BaseModel):
    answer: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    cited_chunk_ids: list[str] = Field(default_factory=list)
    related_assets: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
