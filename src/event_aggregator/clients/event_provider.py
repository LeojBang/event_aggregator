import time
from urllib.parse import urljoin

import httpx

from event_aggregator.core.metrics import (
    events_provider_request_duration_seconds,
    events_provider_requests_total,
)


class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str, client=None):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = client or httpx.AsyncClient()

    async def events(self, changed_at: str, *, url: str | None = None) -> dict | None:
        endpoint = "/events"
        start = time.monotonic()
        status = 500
        headers = {"x-api-key": self._api_key}
        try:
            if url is not None:
                response = await self._client.get(url, headers=headers)
            else:
                response = await self._client.get(
                    urljoin(self._base_url, "/api/events/"),
                    params={"changed_at": changed_at},
                    headers=headers,
                )
            status = response.status_code
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise
        except httpx.RequestError:
            status = 503
            raise
        finally:
            self._record(endpoint, status, time.monotonic() - start)

    async def seats(self, event_id: str) -> dict | None:
        endpoint = "/seats"
        start = time.monotonic()
        status = 500
        headers = {"x-api-key": self._api_key}
        try:
            response = await self._client.get(
                urljoin(self._base_url, f"/api/events/{event_id}/seats/"),
                headers=headers,
            )
            status = response.status_code
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise
        except httpx.RequestError:
            status = 503
            raise
        finally:
            self._record(endpoint, status, time.monotonic() - start)

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> dict | None:
        endpoint = "/registration"
        start = time.monotonic()
        status = 500
        headers = {"x-api-key": self._api_key}
        body = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        try:
            response = await self._client.post(
                urljoin(self._base_url, f"/api/events/{event_id}/register/"),
                json=body,
                headers=headers,
            )
            status = response.status_code
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise
        except httpx.RequestError:
            status = 503
            raise
        finally:
            self._record(endpoint, status, time.monotonic() - start)

    async def unregister(self, event_id: str, ticket_id: str) -> dict | None:
        endpoint = "/registration"
        start = time.monotonic()
        status = 500
        headers = {"x-api-key": self._api_key}
        body = {"ticket_id": ticket_id}
        try:
            response = await self._client.request(
                "DELETE",
                urljoin(self._base_url, f"/api/events/{event_id}/unregister/"),
                json=body,
                headers=headers,
            )
            status = response.status_code
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise
        except httpx.RequestError:
            status = 503
            raise
        finally:
            self._record(endpoint, status, time.monotonic() - start)

    def _record(self, endpoint: str, status: int, duration: float) -> None:
        events_provider_requests_total.labels(
            endpoint=endpoint,
            status=str(status),
        ).inc()
        events_provider_request_duration_seconds.labels(
            endpoint=endpoint,
        ).observe(duration)
