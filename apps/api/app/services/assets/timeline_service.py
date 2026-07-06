from app.domain.assets.schemas import DigitalTwinRecommendation, TimelineEvent
from app.domain.graph.schemas import AssetContext


class TimelineService:
    def build(
        self,
        context: AssetContext,
        maintenance_history: list[TimelineEvent],
        recommendations: list[DigitalTwinRecommendation],
    ) -> list[TimelineEvent]:
        events = list(maintenance_history)
        events.extend(
            TimelineEvent(
                event_type="Incident",
                title=str(node.properties.get("name") or node.properties.get("incident_id") or "Incident"),
                description="Incident connected to this asset in the knowledge graph.",
                source="Neo4j",
                metadata=node.properties,
            )
            for node in context.connected_incidents
        )
        events.extend(
            TimelineEvent(
                event_type="Recommendation",
                title=recommendation.title,
                description=recommendation.rationale,
                source="Gemini" if recommendation.rationale else "Rules",
                metadata={"priority": recommendation.priority},
            )
            for recommendation in recommendations
        )
        return sorted(events, key=lambda event: event.timestamp or "", reverse=True)

