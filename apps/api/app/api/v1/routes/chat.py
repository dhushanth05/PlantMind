from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.chat.schemas import ChatRequest, ChatResponse
from app.services.chat.chat_service import ChatService

router = APIRouter()


@router.get("/health")
async def chat_health() -> dict[str, str]:
    return {"module": "chat", "status": "ready"}


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    return await service.respond(request)
