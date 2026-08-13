from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.core.config import settings
from event_aggregator.core.db import get_db
from event_aggregator.repositories.events import EventRepository
from event_aggregator.repositories.places import PlaceRepository
from event_aggregator.repositories.sync_metadata import SyncMetadataRepository
from event_aggregator.services.sync import SyncService

router = APIRouter(prefix="/api")


@router.post("/sync/trigger")
async def trigger_sync(session: AsyncSession = Depends(get_db)):
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
