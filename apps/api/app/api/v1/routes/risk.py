from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.risk.schemas import RiskDashboardResponse
from app.services.risk_dashboard_service import RiskDashboardService

router = APIRouter()


@router.get("/health")
async def risk_health() -> dict[str, str]:
    return {"module": "risk", "status": "scaffolded"}


def get_risk_dashboard_service() -> RiskDashboardService:
    return RiskDashboardService()


@router.get("/dashboard", response_model=RiskDashboardResponse)
async def risk_dashboard(
    service: Annotated[RiskDashboardService, Depends(get_risk_dashboard_service)],
) -> RiskDashboardResponse:
    return await service.get_dashboard()
