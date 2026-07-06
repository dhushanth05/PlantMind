from pydantic import BaseModel, Field


class ExecutiveKpi(BaseModel):
    label: str
    value: str
    change: str
    tone: str = "neutral"


class SeriesPoint(BaseModel):
    label: str
    value: int


class DistributionItem(BaseModel):
    label: str
    value: int


class AnalyticsInsight(BaseModel):
    title: str
    summary: str
    priority: str = "Medium"


class ExecutiveAnalyticsResponse(BaseModel):
    kpis: list[ExecutiveKpi]
    knowledge_growth: list[SeriesPoint]
    incident_trends: list[SeriesPoint]
    asset_health_distribution: list[DistributionItem]
    failure_distribution: list[DistributionItem]
    operational_insights: list[AnalyticsInsight]
    ai_summary: str
