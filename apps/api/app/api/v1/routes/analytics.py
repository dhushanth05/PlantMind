from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.analytics.schemas import ExecutiveAnalyticsResponse
from app.services.executive_analytics_service import ExecutiveAnalyticsService

router = APIRouter()


def get_executive_analytics_service() -> ExecutiveAnalyticsService:
    return ExecutiveAnalyticsService()


@router.get("/dashboard", response_model=ExecutiveAnalyticsResponse)
async def analytics_dashboard(
    service: Annotated[ExecutiveAnalyticsService, Depends(get_executive_analytics_service)],
) -> ExecutiveAnalyticsResponse:
    return await service.get_dashboard()
