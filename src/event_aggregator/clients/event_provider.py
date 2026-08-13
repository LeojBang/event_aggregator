import httpx


class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str, client=None):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = client or httpx.AsyncClient()

    async def events(self, changed_at: str, *, url: str | None = None) -> dict:
        headers = {"x-api-key": self._api_key}

        if url is not None:
            response = await self._client.get(url, headers=headers)
        else:
            response = await self._client.get(
                f"{self._base_url}/api/events/",
                params={"changed_at": changed_at},
                headers=headers,
            )

        response.raise_for_status()
        return response.json()

    async def seats(self, event_id: str) -> dict:
        headers = {"x-api-key": self._api_key}
        response = await self._client.get(
            f"{self._base_url}/api/events/{event_id}/seats/",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> dict:
        headers = {"x-api-key": self._api_key}
        body = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        response = await self._client.post(
            f"{self._base_url}/api/events/{event_id}/register/",
            json=body,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def unregister(self, event_id: str, ticket_id: str) -> dict:
        headers = {"x-api-key": self._api_key}
        body = {"ticket_id": ticket_id}

        response = await self._client.request(
            "DELETE",
            f"{self._base_url}/api/events/{event_id}/unregister/",
            json=body,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
