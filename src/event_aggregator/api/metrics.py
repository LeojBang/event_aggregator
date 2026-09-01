import asyncio

from fastapi import APIRouter, Depends
from prometheus_client import REGISTRY, generate_latest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from event_aggregator.core.db import get_db
from event_aggregator.core.metrics import (
    events_total,
    tickets_cancelled_total,
    tickets_created_total,
)
from event_aggregator.repositories.events import EventRepository
from event_aggregator.repositories.tickets import TicketRepository

router = APIRouter()


@router.get("/metrics")
async def metrics(session: AsyncSession = Depends(get_db)):
    event_repo = EventRepository(session)
    ticket_repo = TicketRepository(session)

    events_count, tickets_count, cancelled_count = await asyncio.gather(
        event_repo.count(),
        ticket_repo.count(),
        ticket_repo.count_cancelled(),
    )

    events_total.set(events_count)
    tickets_created_total.set(tickets_count)
    tickets_cancelled_total.set(cancelled_count)

    return Response(content=generate_latest(REGISTRY), media_type="text/plain")
