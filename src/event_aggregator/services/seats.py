import time

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.exceptions import EventNotFoundError, EventNotPublishedError
from event_aggregator.models.enums import EventStatus
from event_aggregator.repositories.events import EventRepository


class SeatsService:
    CACHE_TTL_SECONDS = 30

    def __init__(
        self,
        event_repo: EventRepository,
        client: EventsProviderClient,
    ) -> None:
        self._event_repo = event_repo
        self._client = client
        self._cache: dict[str, tuple[list[str], float]] = {}

    async def get_available_seats(self, event_id: str) -> list[str]:
        event = await self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError
        if event.status != EventStatus.PUBLISHED.value:
            raise EventNotPublishedError

        cached = self._cache.get(event_id)
        now = time.monotonic()
        if cached is not None:
            seats, cached_at = cached
            if now - cached_at < self.CACHE_TTL_SECONDS:
                return seats

        response = await self._client.seats(event_id)
        seats = response["seats"]
        self._cache[event_id] = (seats, now)
        return seats
