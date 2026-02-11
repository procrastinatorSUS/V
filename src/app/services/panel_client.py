from __future__ import annotations

import uuid
from datetime import datetime, timedelta, UTC

import httpx


class PanelClient:
    def __init__(self, base_url: str, username: str, password: str, inbound_id: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.inbound_id = inbound_id
        self._client = httpx.AsyncClient(timeout=15)

    async def _login(self) -> None:
        response = await self._client.post(
            f"{self.base_url}/login",
            data={"username": self.username, "password": self.password},
        )
        response.raise_for_status()

    async def issue_vless_key(self, days: int, user_tag: str) -> str:
        await self._login()
        client_id = str(uuid.uuid4())
        expire_at = int((datetime.now(UTC) + timedelta(days=days)).timestamp() * 1000)
        payload = {
            "id": self.inbound_id,
            "settings": {
                "clients": [
                    {
                        "id": client_id,
                        "email": user_tag,
                        "limitIp": 2,
                        "totalGB": 0,
                        "expiryTime": expire_at,
                        "enable": True,
                    }
                ]
            },
        }
        response = await self._client.post(f"{self.base_url}/panel/api/inbounds/addClient", json=payload)
        response.raise_for_status()
        return client_id

    async def close(self) -> None:
        await self._client.aclose()
