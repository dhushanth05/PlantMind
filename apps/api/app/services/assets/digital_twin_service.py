import logging

from app.core.config import settings
from app.db.redis.cache import RedisCache
from app.domain.assets.schemas import AssetDigitalTwin, GraphSummary
from app.services.assets.asset_service import AssetService
from app.services.assets.health_score_service import HealthScoreService
from app.services.assets.recommendation_service import RecommendationService
from app.services.assets.risk_service import RiskService
from app.services.assets.timeline_service import TimelineService

logger = logging.getLogger(__name__)


class DigitalTwinService:
    def __init__(
        self,
        asset_service: AssetService | None = None,
        health_service: HealthScoreService | None = None,
        risk_service: RiskService | None = None,
        timeline_service: TimelineService | None = None,
        recommendation_service: RecommendationService | None = None,
        cache: RedisCache | None = None,
    ) -> None:
        self.asset_service = asset_service or AssetService()
        self.health_service = health_service or HealthScoreService()
        self.risk_service = risk_service or RiskService()
        self.timeline_service = timeline_service or TimelineService()
        self.recommendation_service = recommendation_service or RecommendationService()
        self.cache = cache or RedisCache()

    async def get_digital_twin(self, asset_id: str) -> AssetDigitalTwin:
        cache_key = self._cache_key(asset_id)
        cached = await self.cache.get_json(cache_key)
        if isinstance(cached, dict):
            return AssetDigitalTwin.model_validate(cached)

        context = await self.asset_service.get_asset_context(asset_id)
        maintenance_history = await self.asset_service.get_maintenance_history(asset_id)
        inspection_findings = await self.asset_service.get_inspection_findings(asset_id)
        retrieval_context = await self.asset_service.get_retrieval_context(asset_id)
        graph_degree = len(context.relationships)

        health = self.health_service.compute(
            context=context,
            maintenance_history=maintenance_history,
            inspection_findings=inspection_findings,
            graph_degree=graph_degree,
        )
        risk = self.risk_service.assess(context=context, health_score=health, graph_degree=graph_degree)
        recommendations = await self.recommendation_service.generate(
            asset_id=asset_id,
            context=context,
            retrieval_context=retrieval_context,
            risk=risk,
        )
        timeline = self.timeline_service.build(
            context=context,
            maintenance_history=maintenance_history,
            recommendations=recommendations,
        )
        twin = AssetDigitalTwin(
            asset=context.equipment,
            health_score=health,
            risk_level=risk,
            maintenance_history=maintenance_history,
            incidents=context.connected_incidents,
            connected_documents=context.connected_documents,
            procedures=context.related_procedures,
            assigned_personnel=context.connected_personnel,
            failure_modes=context.failure_modes,
            recommendations=recommendations,
            graph_summary=GraphSummary(
                connected_nodes=len(retrieval_context.graph_context.related_nodes),
                connected_documents=len(context.connected_documents),
                connected_engineers=len(context.connected_personnel),
                failure_modes=len(context.failure_modes),
                procedures=len(context.related_procedures),
            ),
            related_assets=self.asset_service.related_assets(context, retrieval_context.graph_context.related_nodes),
            operational_timeline=timeline,
        )
        await self.cache.set_json(cache_key, twin.model_dump(mode="json"), settings.digital_twin_cache_ttl_seconds)
        logger.info("digital_twin_created", extra={"asset_id": asset_id, "health": health.score, "risk": risk.level})
        return twin

    @staticmethod
    def _cache_key(asset_id: str) -> str:
        return f"digital_twin:{asset_id}"

