import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from event_aggregator.core.metrics import (
    http_request_duration_seconds,
    http_requests_total,
)


# Middleware для метрик
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - start
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=str(response.status_code),
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)
        return response
