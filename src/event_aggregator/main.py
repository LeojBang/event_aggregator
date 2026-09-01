import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration

from event_aggregator.api.events import router as events_router
from event_aggregator.api.health import router as health_router
from event_aggregator.api.metrics import router as metrics_router
from event_aggregator.api.sync import router as sync_router
from event_aggregator.api.sync import sync_lifespan
from event_aggregator.api.tickets import router as tickets_router
from event_aggregator.core.config import settings
from event_aggregator.middleware.metrics import MetricsMiddleware

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
    )
app = FastAPI(lifespan=sync_lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    if request.method == "POST" and request.url.path == "/api/tickets":
        return JSONResponse(status_code=400, content={"detail": exc.errors()})
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.add_middleware(MetricsMiddleware)
app.include_router(health_router)
app.include_router(sync_router)
app.include_router(events_router)
app.include_router(tickets_router)
app.include_router(metrics_router)
