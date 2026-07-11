from typing import Annotated
import logging

from fastapi import APIRouter, Depends

from app.domain.dashboard.schemas import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_dashboard_service() -> DashboardService:
    return DashboardService()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    logger.info("dashboard_route_start")
    response = await service.get_dashboard()
    logger.info(
        "dashboard_route_complete",
        extra={
            "stats": len(response.stats),
            "activities": len(response.activities),
            "alerts": len(response.alerts),
            "uploads": len(response.recent_uploads),
        },
    )
    return response
