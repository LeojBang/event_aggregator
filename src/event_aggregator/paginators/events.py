from event_aggregator.clients.event_provider import EventsProviderClient


class EventsPaginator:
    DEFAULT_CHANGED_AT = "2000-01-01"

    def __init__(self, client: EventsProviderClient, changed_at=DEFAULT_CHANGED_AT):
        self._client = client
        self._changed_at = changed_at

    async def __aiter__(self):
        next_url = None

        while True:
            page = await self._client.events(changed_at=self._changed_at, url=next_url)

            for event in page["results"]:
                yield event

            next_url = page.get("next")
            if next_url is None:
                break
