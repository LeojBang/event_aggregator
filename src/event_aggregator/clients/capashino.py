from urllib.parse import urljoin

import httpx


class CapashinoClient:
    def __init__(self, base_url: str, api_key: str, client=None):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = client or httpx.AsyncClient()

    async def send_notification(
        self, *, message: str, reference_id: str, idempotency_key: str
    ) -> dict:
        headers = {"Content-Type": "application/json", "x-api-key": self._api_key}
        body = {
            "message": message,
            "reference_id": reference_id,
            "idempotency_key": idempotency_key,
        }

        response = await self._client.post(
            urljoin(self._base_url, "/api/notifications"), json=body, headers=headers
        )
        response.raise_for_status()
        return response.json()
