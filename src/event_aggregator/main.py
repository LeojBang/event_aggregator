from fastapi import FastAPI

from event_aggregator.api.events import router as events_router
from event_aggregator.api.health import router as health_router
from event_aggregator.api.sync import router as sync_router
from event_aggregator.api.sync import sync_lifespan
from event_aggregator.api.tickets import router as tickets_router

app = FastAPI(lifespan=sync_lifespan)
app.include_router(health_router)
app.include_router(sync_router)
app.include_router(events_router)
app.include_router(tickets_router)
