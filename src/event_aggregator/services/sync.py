import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.paginators.events import EventsPaginator
from event_aggregator.repositories.events import EventRepository
from event_aggregator.repositories.places import PlaceRepository
from event_aggregator.repositories.sync_metadata import SyncMetadataRepository

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(
        self,
        session: AsyncSession,
        place_repo: PlaceRepository,
        event_repo: EventRepository,
        sync_repo: SyncMetadataRepository,
        client: EventsProviderClient,
    ) -> None:
        self._session = session
        self._place_repo = place_repo
        self._event_repo = event_repo
        self._sync_repo = sync_repo
        self._client = client

    async def run(self) -> None:
        metadata = await self._sync_repo.get()
        previous_last_changed_at = metadata.last_changed_at if metadata else None

        if previous_last_changed_at is None:
            changed_at = EventsPaginator.DEFAULT_CHANGED_AT
        else:
            changed_at = previous_last_changed_at.strftime("%Y-%m-%d")

        logger.info("Starting sync with changed_at=%s", changed_at)

        try:
            await self._sync_repo.save(
                datetime.now(UTC),
                previous_last_changed_at,
                "running",
            )

            max_changed_at = previous_last_changed_at

            async for event in EventsPaginator(self._client, changed_at=changed_at):
                await self._place_repo.upsert(event["place"])
                await self._event_repo.upsert(event)

                event_changed_at = datetime.fromisoformat(event["changed_at"])
                if max_changed_at is None or event_changed_at > max_changed_at:
                    max_changed_at = event_changed_at

            await self._sync_repo.save(datetime.now(UTC), max_changed_at, "idle")
            await self._session.commit()
            logger.info("Sync completed successfully")
        except Exception:
            logger.exception("Sync failed")
            await self._session.rollback()
            await self._sync_repo.save(
                datetime.now(UTC),
                previous_last_changed_at,
                "error",
            )
            await self._session.commit()
            raise
