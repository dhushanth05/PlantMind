from app.domain.assets.schemas import HealthScore, TimelineEvent
from app.domain.graph.schemas import AssetContext


class HealthScoreService:
    def compute(
        self,
        context: AssetContext,
        maintenance_history: list[TimelineEvent],
        inspection_findings: list[dict],
        graph_degree: int,
    ) -> HealthScore:
        incident_penalty = min(35, len(context.connected_incidents) * 8)
        failure_penalty = min(25, len(context.failure_modes) * 7)
        maintenance_credit = min(12, len(maintenance_history) * 2)
        centrality_penalty = min(12, max(graph_degree - 8, 0))
        inspection_penalty = min(16, sum(self._inspection_penalty(finding) for finding in inspection_findings))
        score = max(0, min(100, 88 - incident_penalty - failure_penalty - centrality_penalty - inspection_penalty + maintenance_credit))
        return HealthScore(score=score, status=self._status(score))

    @staticmethod
    def _inspection_penalty(finding: dict) -> int:
        severity = str(finding.get("severity", "")).lower()
        if severity in {"critical", "high"}:
            return 8
        if severity == "medium":
            return 4
        return 2 if finding else 0

    @staticmethod
    def _status(score: int) -> str:
        if score >= 80:
            return "Healthy"
        if score >= 60:
            return "Watch"
        if score >= 40:
            return "Degraded"
        return "Critical"

