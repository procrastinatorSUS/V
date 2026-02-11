from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware

from app.config import get_settings
from app.db.session import SessionLocal
from app.services.panel_client import PanelClient
from app.services.security import build_cipher


class ServicesMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cipher = build_cipher(self.settings.encryption_key.get_secret_value())
        self.panel_client = PanelClient(
            base_url=self.settings.panel_url,
            username=self.settings.panel_username,
            password=self.settings.panel_password.get_secret_value(),
            inbound_id=self.settings.panel_inbound_id,
        )

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with SessionLocal() as session:
            data["session"] = session
            data["cipher"] = self.cipher
            data["panel_client"] = self.panel_client
            result = await handler(event, data)
            return result
