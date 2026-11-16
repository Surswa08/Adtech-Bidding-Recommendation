from datetime import datetime, timezone
from app.services.event_bus import EventBus
from app.services.feature_store import FeatureStore

class FeedbackService:
    def __init__(self, feature_store: FeatureStore, event_bus: EventBus):
        self.features = feature_store
        self.events = event_bus
        self.impressions = {}  # Demo only; use durable storage in production.

    async def record_impression(self, decision: dict, user_id: str):
        self.impressions[decision["impression_id"]] = {
            **decision, "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "clicked": False, "converted": False, "label_status": "pending"
        }
        await self.features.increment(f"user:{user_id}", "user_impressions")
        await self.events.publish({"event_type":"impression", **decision, "user_id":user_id})

    async def click(self, impression_id: str, user_id: str):
        item = self.impressions.get(impression_id)
        if not item:
            return False
        item["clicked"] = True
        await self.features.increment(f"user:{user_id}", "user_clicks")
        await self.events.publish({
            "event_type":"click", "impression_id":impression_id,
            "campaign_id":item["campaign_id"], "user_id":user_id,
            "event_timestamp":datetime.now(timezone.utc).isoformat()
        })
        return True

    async def conversion(self, impression_id: str, user_id: str, value):
        item = self.impressions.get(impression_id)
        if not item:
            return False
        item["converted"] = True
        item["label_status"] = "positive"
        item["conversion_value"] = value
        await self.events.publish({
            "event_type":"conversion", "impression_id":impression_id,
            "campaign_id":item["campaign_id"], "user_id":user_id,
            "conversion_value":value,
            "event_timestamp":datetime.now(timezone.utc).isoformat()
        })
        return True
