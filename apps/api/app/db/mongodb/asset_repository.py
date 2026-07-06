from typing import Any

from app.db.mongodb.client import mongo_database
from app.domain.assets.schemas import TimelineEvent


class AssetRepository:
    def __init__(self) -> None:
        self.db = mongo_database.database

    async def get_maintenance_history(self, asset_id: str, limit: int = 50) -> list[TimelineEvent]:
        cursor = (
            self.db.asset_events.find(
                {"asset_id": asset_id, "event_type": {"$in": ["Inspection", "Maintenance", "Repair"]}},
                {"_id": 0},
            )
            .sort("timestamp", -1)
            .limit(limit)
        )
        return [self._event_from_document(document) async for document in cursor]

    async def get_inspection_findings(self, asset_id: str, limit: int = 50) -> list[dict[str, Any]]:
        cursor = (
            self.db.asset_events.find(
                {"asset_id": asset_id, "event_type": "Inspection"},
                {"_id": 0, "title": 1, "description": 1, "severity": 1, "timestamp": 1},
            )
            .sort("timestamp", -1)
            .limit(limit)
        )
        return [document async for document in cursor]

    @staticmethod
    def _event_from_document(document: dict[str, Any]) -> TimelineEvent:
        return TimelineEvent(
            event_type=document.get("event_type", "Maintenance"),
            title=document.get("title", "Asset event"),
            description=document.get("description", ""),
            timestamp=str(document["timestamp"]) if document.get("timestamp") is not None else None,
            source=document.get("source"),
            metadata={key: value for key, value in document.items() if key not in {"event_type", "title", "description", "timestamp", "source"}},
        )

