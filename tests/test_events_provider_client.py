import asyncio
from unittest.mock import AsyncMock, MagicMock

from event_aggregator.clients.event_provider import EventsProviderClient


def _fake_response(data: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = data
    response.raise_for_status = MagicMock()
    return response


def test_events_first_page():
    asyncio.run(_test_events_first_page())


async def _test_events_first_page():
    # 1. фейковый httpx
    mock_http = AsyncMock()

    # 2. что "вернёт API"
    mock_http.get.return_value = _fake_response(
        {
            "next": None,
            "previous": None,
            "results": [{"id": "event-1"}],
        }
    )

    # 3. твой client с подменённым httpx
    client = EventsProviderClient(
        base_url="http://test-provider",
        api_key="secret-key",
        client=mock_http,
    )

    # 4. вызов
    result = await client.events("2026-01-01")

    # 5. проверки
    mock_http.get.assert_awaited_once_with(
        "http://test-provider/api/events/",
        params={"changed_at": "2026-01-01"},
        headers={"x-api-key": "secret-key"},
    )
    assert result["results"] == [{"id": "event-1"}]


async def _test_events_follows_next_url():
    mock_http = AsyncMock()

    mock_http.get.return_value = _fake_response(
        {
            "next": None,
            "previous": None,
            "results": [{"id": "event-10"}],
        }
    )

    client = EventsProviderClient(
        base_url="http://test-provider",
        api_key="secret-key",
        client=mock_http,
    )

    await client.events("2026-01-01", url="http://test-provider/page-2")

    mock_http.get.assert_awaited_once_with(
        "http://test-provider/page-2",
        headers={"x-api-key": "secret-key"},
    )


def test_events_follows_next_url():
    asyncio.run(_test_events_follows_next_url())


async def _test_register():
    mock_http = AsyncMock()

    mock_http.post.return_value = _fake_response(
        {
            "ticket_id": "ticket-1",
        }
    )

    client = EventsProviderClient(
        base_url="http://test-provider",
        api_key="secret-key",
        client=mock_http,
    )

    await client.register("event-1", "Ivan", "Ivanov", "ivan@example.com", "A15")

    mock_http.post.assert_awaited_once_with(
        "http://test-provider/api/events/event-1/register/",
        json={
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "email": "ivan@example.com",
            "seat": "A15",
        },
        headers={"x-api-key": "secret-key"},
    )


def test_register():
    asyncio.run(_test_register())


async def _test_unregister():
    mock_http = AsyncMock()

    mock_http.request.return_value = _fake_response(
        {
            "ticket_id": "ticket-1",
        }
    )

    client = EventsProviderClient(
        base_url="http://test-provider",
        api_key="secret-key",
        client=mock_http,
    )

    await client.unregister("event-1", "ticket-1")

    mock_http.request.assert_awaited_once_with(
        "DELETE",
        "http://test-provider/api/events/event-1/unregister/",
        json={"ticket_id": "ticket-1"},
        headers={"x-api-key": "secret-key"},
    )


def test_unregister():
    asyncio.run(_test_unregister())
