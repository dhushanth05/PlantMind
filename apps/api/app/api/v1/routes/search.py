from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.domain.search.schemas import HybridSearchResponse, SearchQueryRequest
from app.services.search.search_service import SearchService

router = APIRouter()


def get_search_service() -> SearchService:
    return SearchService()


@router.post("/query", response_model=HybridSearchResponse)
async def search_query(
    request: SearchQueryRequest,
    service: Annotated[SearchService, Depends(get_search_service)],
) -> HybridSearchResponse:
    top_k = request.top_k or settings.hybrid_search_top_k
    return await service.query(query=request.query, top_k=top_k)
