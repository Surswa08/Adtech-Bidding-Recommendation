import time
import uuid
from app.core.config import settings
from app.services.retrieval import retrieve_candidates
from app.services.bidding import expected_value_and_bid
from app.services.ranker import choose_creative, rank_candidates
from app.models.predictor import Predictor

class DecisionEngine:
    def __init__(self, feature_store):
        self.feature_store = feature_store
        self.predictor = Predictor()

    async def decide(self, request):
        started = time.perf_counter()
        candidates = retrieve_candidates(request, settings.max_candidates)
        scored = []
        user_features = await self.feature_store.get(f"user:{request.user_id}", {})
        for campaign in candidates:
            ctr, cvr = self.predictor.predict(request, campaign, user_features)
            value, bid = expected_value_and_bid(campaign, ctr, cvr)
            creative = choose_creative(campaign, request)
            if creative:
                scored.append({
                    "campaign": campaign, "ctr": ctr, "cvr": cvr,
                    "expected_value": value, "bid": bid, "creative": creative
                })
        ranked = rank_candidates(scored)
        if not ranked:
            return None
        winner = ranked[0]
        latency = (time.perf_counter() - started) * 1000
        return {
            "request_id": request.request_id,
            "impression_id": f"imp_{uuid.uuid4().hex[:16]}",
            "campaign_id": winner["campaign"].campaign_id,
            "ad_id": winner["campaign"].ad_id,
            "creative_id": winner["creative"]["creative_id"],
            "predicted_ctr": round(winner["ctr"], 6),
            "predicted_cvr": round(winner["cvr"], 6),
            "bid_price": round(winner["bid"], 4),
            "currency": "EUR",
            "expected_value": round(winner["expected_value"], 6),
            "decision_latency_ms": round(latency, 3),
            "model_version": self.predictor.version
        }
