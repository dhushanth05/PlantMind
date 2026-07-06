from typing import Literal

from pydantic import BaseModel, Field


ComplianceSeverity = Literal["Low", "Medium", "High", "Critical"]


class ComplianceOverview(BaseModel):
    score: int = Field(ge=0, le=100)
    status: str
    total_documents: int
    mapped_regulations: int
    open_gaps: int
    inspections_due: int


class ComplianceItem(BaseModel):
    id: str
    title: str
    asset_id: str | None = None
    severity: ComplianceSeverity = "Medium"
    due_date: str | None = None
    source: str | None = None


class RegulatoryMapping(BaseModel):
    framework: str
    mapped_documents: int
    gaps: int
    status: str


class ComplianceRecommendation(BaseModel):
    id: str
    title: str
    rationale: str
    priority: ComplianceSeverity
    copilot_query: str


class ComplianceDashboardResponse(BaseModel):
    overview: ComplianceOverview
    missing_sops: list[ComplianceItem]
    inspections_due: list[ComplianceItem]
    compliance_gaps: list[ComplianceItem]
    regulatory_mapping: list[RegulatoryMapping]
    recommendations: list[ComplianceRecommendation]
