from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.dashboard.schemas import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


def get_dashboard_service() -> DashboardService:
    return DashboardService()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    return await service.get_dashboard()
