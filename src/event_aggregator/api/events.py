from datetime import date
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.core.config import settings
from event_aggregator.core.db import get_db
from event_aggregator.exceptions import EventNotFoundError, EventNotPublishedError
from event_aggregator.repositories.events import EventRepository
from event_aggregator.schemas.events import (
    EventDetailSchema,
    EventListResponseSchema,
    SeatsResponseSchema,
)
from event_aggregator.services.seats import SeatsService

router = APIRouter()


def _build_events_url(
    request: Request,
    page: int,
    page_size: int,
    date_from: date | None,
) -> str:
    params: dict[str, str | int] = {"page": page, "page_size": page_size}
    if date_from is not None:
        params["date_from"] = date_from.isoformat()
    base = str(request.base_url).rstrip("/")
    return f"{base}/api/events/?{urlencode(params)}"


def _get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        settings.EVENTS_PROVIDER_URL,
        settings.EVENTS_PROVIDER_API_KEY,
    )


@router.get("/api/events", response_model=EventListResponseSchema)
async def list_events(
    request: Request,
    session: AsyncSession = Depends(get_db),
    date_from: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
) -> EventListResponseSchema:
    repo = EventRepository(session)
    count = await repo.count(date_from)
    offset = (page - 1) * page_size
    events = await repo.list(date_from=date_from, offset=offset, limit=page_size)

    next_url = None
    if offset + len(events) < count:
        next_url = _build_events_url(request, page + 1, page_size, date_from)

    previous_url = None
    if page > 1:
        previous_url = _build_events_url(request, page - 1, page_size, date_from)

    return EventListResponseSchema(
        count=count,
        next=next_url,
        previous=previous_url,
        results=events,
    )


@router.get("/api/events/{event_id}", response_model=EventDetailSchema)
async def get_event(
    event_id: str,
    session: AsyncSession = Depends(get_db),
) -> EventDetailSchema:
    repo = EventRepository(session)
    event = await repo.get_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventDetailSchema.model_validate(event)


@router.get("/api/events/{event_id}/seats", response_model=SeatsResponseSchema)
async def get_event_seats(
    event_id: str,
    session: AsyncSession = Depends(get_db),
) -> SeatsResponseSchema:
    client = _get_events_provider_client()
    service = SeatsService(EventRepository(session), client)
    try:
        seats = await service.get_available_seats(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Event not found") from exc
    except EventNotPublishedError as exc:
        raise HTTPException(status_code=400, detail="Event is not published") from exc

    return SeatsResponseSchema(event_id=event_id, available_seats=seats)
