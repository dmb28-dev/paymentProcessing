from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="payment-processing-service", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    api_key: str = Field(default="dev-secret-key", alias="API_KEY")
    database_url: str = Field(
        default="postgresql+asyncpg://payments:payments@localhost:5432/payments",
        alias="DATABASE_URL",
    )
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672/", alias="RABBITMQ_URL")
    outbox_poll_interval_seconds: int = Field(default=1, alias="OUTBOX_POLL_INTERVAL_SECONDS")
    webhook_timeout_seconds: int = Field(default=5, alias="WEBHOOK_TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
