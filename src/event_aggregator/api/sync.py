import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.core.config import settings
from event_aggregator.core.db import SessionLocal, get_db
from event_aggregator.repositories.events import EventRepository
from event_aggregator.repositories.places import PlaceRepository
from event_aggregator.repositories.sync_metadata import SyncMetadataRepository
from event_aggregator.services.sync import SyncService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _run_scheduled_sync() -> None:
    while True:
        await asyncio.sleep(86400)
        try:
            async with SessionLocal() as session:
                client = EventsProviderClient(
                    settings.EVENTS_PROVIDER_URL,
                    settings.EVENTS_PROVIDER_API_KEY,
                )
                service = SyncService(
                    session,
                    PlaceRepository(session),
                    EventRepository(session),
                    SyncMetadataRepository(session),
                    client,
                )
                await service.run()
        except Exception:
            logger.exception("Scheduled sync failed")


@router.post("/api/sync/trigger")
async def trigger_sync(session: AsyncSession = Depends(get_db)) -> dict[str, str]:
    client = EventsProviderClient(
        settings.EVENTS_PROVIDER_URL,
        settings.EVENTS_PROVIDER_API_KEY,
    )
    service = SyncService(
        session,
        PlaceRepository(session),
        EventRepository(session),
        SyncMetadataRepository(session),
        client,
    )
    await service.run()
    return {"status": "ok"}


@asynccontextmanager
async def sync_lifespan(app):  # noqa: ARG001
    task = asyncio.create_task(_run_scheduled_sync())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
