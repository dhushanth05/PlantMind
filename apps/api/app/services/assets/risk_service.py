from app.domain.assets.schemas import HealthScore, RiskAssessment
from app.domain.graph.schemas import AssetContext


class RiskService:
    def assess(self, context: AssetContext, health_score: HealthScore, graph_degree: int) -> RiskAssessment:
        risk_score = min(
            100,
            (100 - health_score.score)
            + len(context.connected_incidents) * 7
            + len(context.failure_modes) * 6
            + max(graph_degree - 10, 0),
        )
        level = self._level(risk_score)
        reasons = []
        if context.connected_incidents:
            reasons.append(f"{len(context.connected_incidents)} connected incident(s)")
        if context.failure_modes:
            reasons.append(f"{len(context.failure_modes)} recurring failure mode(s)")
        if graph_degree > 10:
            reasons.append("high graph centrality")
        if not reasons:
            reasons.append("limited adverse evidence in the current graph context")
        return RiskAssessment(level=level, score=risk_score, explanation=f"{level} risk due to " + ", ".join(reasons) + ".")

    @staticmethod
    def _level(score: int) -> str:
        if score >= 80:
            return "Critical"
        if score >= 55:
            return "High"
        if score >= 30:
            return "Medium"
        return "Low"

