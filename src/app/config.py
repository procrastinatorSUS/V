from functools import lru_cache
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: SecretStr = Field(alias="BOT_TOKEN")
    admin_ids: str = Field(alias="ADMIN_IDS", description="Comma-separated Telegram user IDs")
    provider_token: SecretStr = Field(alias="PROVIDER_TOKEN")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL", default="redis://localhost:6379/0")

    base_monthly_price: int = Field(alias="BASE_MONTHLY_PRICE", default=500)
    yearly_discount_percent: int = Field(alias="YEARLY_DISCOUNT_PERCENT", default=20)

    panel_url: str = Field(alias="PANEL_URL")
    panel_username: str = Field(alias="PANEL_USERNAME")
    panel_password: SecretStr = Field(alias="PANEL_PASSWORD")
    panel_inbound_id: int = Field(alias="PANEL_INBOUND_ID")

    encryption_key: SecretStr = Field(alias="ENCRYPTION_KEY")

    @property
    def admin_id_set(self) -> set[int]:
        return {int(item.strip()) for item in self.admin_ids.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
