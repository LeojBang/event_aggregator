import asyncio
from unittest.mock import AsyncMock

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.paginators.events import EventsPaginator


async def _collect(paginator):
    result = []
    async for event in paginator:
        result.append(event)
    return result


def test_paginator_yields_all_events():
    asyncio.run(_test_paginator_yields_all_events())


async def _test_paginator_yields_all_events():
    # 1. фейковый client (не httpx)
    mock_client = AsyncMock(spec=EventsProviderClient)

    # 2. две "страницы" API
    mock_client.events = AsyncMock(
        side_effect=[
            {
                "next": "http://test-provider/page-2",
                "results": [{"id": "1"}, {"id": "2"}],
            },
            {
                "next": None,
                "results": [{"id": "3"}],
            },
        ]
    )

    # 3. paginator
    paginator = EventsPaginator(mock_client)

    # 4. собрать события
    events = await _collect(paginator)

    # 5. проверки
    calls = mock_client.events.await_args_list
    assert calls[1].kwargs["url"] == "http://test-provider/page-2"
    assert [e["id"] for e in events] == ["1", "2", "3"]
    assert mock_client.events.await_count == 2
