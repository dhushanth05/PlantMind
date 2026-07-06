from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.alerts.schemas import AlertsDashboardResponse
from app.services.alerts_dashboard_service import AlertsDashboardService

router = APIRouter()


@router.get("/health")
async def alerts_health() -> dict[str, str]:
    return {"module": "alerts", "status": "scaffolded"}


def get_alerts_dashboard_service() -> AlertsDashboardService:
    return AlertsDashboardService()


@router.get("/dashboard", response_model=AlertsDashboardResponse)
async def alerts_dashboard(
    service: Annotated[AlertsDashboardService, Depends(get_alerts_dashboard_service)],
) -> AlertsDashboardResponse:
    return await service.get_dashboard()
