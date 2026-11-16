from pydantic import BaseModel, Field
from typing import Literal, Optional

class AdRequest(BaseModel):
    request_id: str
    user_id: str
    publisher_id: str
    placement: str
    country: str = "US"
    device: str = "desktop"
    page_category: str = "general"
    consented_personalization: bool = False

class AdDecision(BaseModel):
    request_id: str
    impression_id: str
    campaign_id: str
    ad_id: str
    creative_id: str
    predicted_ctr: float
    predicted_cvr: float
    bid_price: float
    currency: str = "EUR"
    expected_value: float
    decision_latency_ms: float
    model_version: str

class FeedbackEvent(BaseModel):
    impression_id: str
    user_id: str
    conversion_value: Optional[float] = None

class Campaign(BaseModel):
    campaign_id: str
    ad_id: str
    advertiser_id: str
    category: str
    pricing_model: Literal["CPC", "CPA", "CPM"]
    bid: float = Field(gt=0)
    daily_budget: float = Field(gt=0)
    spent_today: float = 0
    active: bool = True
    countries: list[str] = ["FR", "US"]
    devices: list[str] = ["mobile", "desktop"]
    placements: list[str] = ["homepage-banner"]
    creatives: list[dict]
    base_ctr: float = 0.03
    base_cvr: float = 0.04
