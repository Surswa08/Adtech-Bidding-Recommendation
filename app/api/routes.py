from fastapi import APIRouter, HTTPException, Request
from app.schemas.ads import AdRequest, FeedbackEvent
from app.data.catalog import CAMPAIGNS

router = APIRouter()

@router.post("/decide")
async def decide(payload: AdRequest, request: Request):
    result = await request.app.state.engine.decide(payload)
    if result is None:
        raise HTTPException(status_code=404, detail="No eligible ad")
    await request.app.state.feedback.record_impression(result, payload.user_id)
    return result

@router.post("/events/click")
async def click(payload: FeedbackEvent, request: Request):
    ok = await request.app.state.feedback.click(payload.impression_id, payload.user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Unknown impression_id")
    return {"accepted": True, "event_type": "click"}

@router.post("/events/conversion")
async def conversion(payload: FeedbackEvent, request: Request):
    ok = await request.app.state.feedback.conversion(
        payload.impression_id, payload.user_id, payload.conversion_value
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Unknown impression_id")
    return {"accepted": True, "event_type": "conversion", "label_status": "positive"}

@router.get("/campaigns")
async def campaigns():
    return [campaign.model_dump() for campaign in CAMPAIGNS]
