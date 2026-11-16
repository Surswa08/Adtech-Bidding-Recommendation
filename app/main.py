from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import router
from app.services.feature_store import FeatureStore
from app.services.event_bus import EventBus
from app.services.decision_engine import DecisionEngine
from app.services.feedback import FeedbackService

@asynccontextmanager
async def lifespan(app: FastAPI):
    features = FeatureStore()
    await features.connect()
    bus = EventBus()
    await bus.connect()
    app.state.features = features
    app.state.events = bus
    app.state.engine = DecisionEngine(features)
    app.state.feedback = FeedbackService(features, bus)
    yield
    await bus.close()
    await features.close()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status":"ok", "service":settings.app_name}

@app.get("/metrics")
async def metrics():
    return {"note":"Demo counters are maintained in-process; export Prometheus metrics in production."}
