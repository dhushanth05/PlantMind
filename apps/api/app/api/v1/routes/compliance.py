from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.compliance.schemas import ComplianceDashboardResponse
from app.services.compliance_dashboard_service import ComplianceDashboardService

router = APIRouter()


@router.get("/health")
async def compliance_health() -> dict[str, str]:
    return {"module": "compliance", "status": "scaffolded"}


def get_compliance_dashboard_service() -> ComplianceDashboardService:
    return ComplianceDashboardService()


@router.get("/dashboard", response_model=ComplianceDashboardResponse)
async def compliance_dashboard(
    service: Annotated[ComplianceDashboardService, Depends(get_compliance_dashboard_service)],
) -> ComplianceDashboardResponse:
    return await service.get_dashboard()
