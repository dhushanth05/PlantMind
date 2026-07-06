import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.db.mongodb.client import mongo_database
from app.domain.compliance.schemas import (
    ComplianceDashboardResponse,
    ComplianceItem,
    ComplianceOverview,
    ComplianceRecommendation,
    RegulatoryMapping,
)

logger = logging.getLogger(__name__)
DEPENDENCY_TIMEOUT_SECONDS = 2.0
FRAMEWORKS = ["OISD", "PESO", "Factory Act", "Environmental Compliance"]


class ComplianceDashboardService:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def get_dashboard(self) -> ComplianceDashboardResponse:
        total_documents, framework_counts, inspections, gaps = await asyncio.gather(
            self._safe_call(lambda: self._count_collection("documents"), 0),
            self._safe_call(self._framework_counts, {}),
            self._safe_call(self._inspection_rows, []),
            self._safe_call(self._gap_rows, []),
        )
        mappings = [
            RegulatoryMapping(
                framework=framework,
                mapped_documents=int(framework_counts.get(framework, 0)),
                gaps=0 if framework_counts.get(framework, 0) else 1,
                status="Mapped" if framework_counts.get(framework, 0) else "Needs Evidence",
            )
            for framework in FRAMEWORKS
        ]
        open_gaps = len(gaps) + sum(item.gaps for item in mappings)
        score = max(0, min(100, 100 - open_gaps * 8 - len(inspections) * 4))
        recommendations = self._recommendations(mappings=mappings, inspections=inspections, gaps=gaps)
        return ComplianceDashboardResponse(
            overview=ComplianceOverview(
                score=score,
                status="Healthy" if score >= 80 else ("Watch" if score >= 55 else "Action Required"),
                total_documents=total_documents,
                mapped_regulations=sum(1 for item in mappings if item.mapped_documents > 0),
                open_gaps=open_gaps,
                inspections_due=len(inspections),
            ),
            missing_sops=self._missing_sops(gaps),
            inspections_due=[self._item_from_row(row, fallback_title="Inspection due") for row in inspections],
            compliance_gaps=[self._item_from_row(row, fallback_title="Compliance gap") for row in gaps],
            regulatory_mapping=mappings,
            recommendations=recommendations,
        )

    async def _framework_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for framework in FRAMEWORKS:
            counts[framework] = await self.db.documents.count_documents({"filename": {"$regex": framework, "$options": "i"}})
        return counts

    async def _inspection_rows(self) -> list[dict[str, Any]]:
        cursor = (
            self.db.asset_events.find(
                {"event_type": "Inspection", "status": {"$in": ["due", "overdue", "Due", "Overdue"]}},
                {"asset_id": 1, "title": 1, "description": 1, "severity": 1, "timestamp": 1, "source": 1},
            )
            .sort("timestamp", -1)
            .limit(10)
        )
        return [row async for row in cursor]

    async def _gap_rows(self) -> list[dict[str, Any]]:
        cursor = (
            self.db.asset_events.find(
                {"event_type": {"$in": ["ComplianceGap", "Recommendation"]}},
                {"asset_id": 1, "title": 1, "description": 1, "severity": 1, "timestamp": 1, "source": 1},
            )
            .sort("timestamp", -1)
            .limit(10)
        )
        return [row async for row in cursor]

    async def _count_collection(self, collection: str) -> int:
        return int(await self.db[collection].count_documents({}))

    async def _safe_call(self, call, fallback):
        try:
            return await asyncio.wait_for(call(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except TimeoutError:
            logger.warning("compliance_dashboard_dependency_timeout")
            return fallback
        except Exception as exc:
            logger.warning("compliance_dashboard_dependency_failed: %s", exc)
            return fallback

    @staticmethod
    def _missing_sops(gaps: list[dict[str, Any]]) -> list[ComplianceItem]:
        sop_gaps = [row for row in gaps if "sop" in str(row.get("title") or row.get("description") or "").lower()]
        return [ComplianceDashboardService._item_from_row(row, fallback_title="Missing SOP evidence") for row in sop_gaps[:6]]

    @staticmethod
    def _item_from_row(row: dict[str, Any], fallback_title: str) -> ComplianceItem:
        return ComplianceItem(
            id=str(row.get("_id") or row.get("asset_id") or fallback_title),
            title=str(row.get("title") or row.get("description") or fallback_title),
            asset_id=str(row.get("asset_id")) if row.get("asset_id") else None,
            severity=ComplianceDashboardService._severity(row.get("severity") or "Medium"),
            due_date=ComplianceDashboardService._date(row.get("timestamp")),
            source=str(row.get("source")) if row.get("source") else None,
        )

    @staticmethod
    def _recommendations(
        mappings: list[RegulatoryMapping], inspections: list[dict[str, Any]], gaps: list[dict[str, Any]]
    ) -> list[ComplianceRecommendation]:
        recommendations: list[ComplianceRecommendation] = []
        for mapping in mappings:
            if mapping.gaps:
                recommendations.append(
                    ComplianceRecommendation(
                        id=f"mapping-{mapping.framework}",
                        title=f"Map evidence for {mapping.framework}",
                        rationale=f"No documents currently map to {mapping.framework}.",
                        priority="High",
                        copilot_query=f"Which documents satisfy {mapping.framework} compliance?",
                    )
                )
        if inspections:
            recommendations.append(
                ComplianceRecommendation(
                    id="inspection-due",
                    title="Review overdue inspections",
                    rationale=f"{len(inspections)} inspection records are due or overdue.",
                    priority="High",
                    copilot_query="Summarize overdue inspections and required actions.",
                )
            )
        if gaps and not recommendations:
            recommendations.append(
                ComplianceRecommendation(
                    id="compliance-gap",
                    title="Close open compliance gaps",
                    rationale=f"{len(gaps)} compliance gap records are open.",
                    priority="Medium",
                    copilot_query="What evidence is missing for current compliance gaps?",
                )
            )
        return recommendations[:5]

    @staticmethod
    def _severity(value: Any) -> str:
        text = str(value)
        return text if text in {"Low", "Medium", "High", "Critical"} else "Medium"

    @staticmethod
    def _date(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.astimezone(UTC).date().isoformat()
        return str(value)
