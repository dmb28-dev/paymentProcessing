from pydantic import Field

from src.core.config.base import BaseSettings
from src.core.config.database import DatabaseSettings
from src.core.config.log import LogSettings
from src.core.config.rabbitmq import RabbitSettings
from src.core.config.server import ServerSettings
from src.utils.enums import ApplicationEnvironment, AppType


class ApplicationSettings(BaseSettings):

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    app_env: ApplicationEnvironment = Field(default=ApplicationEnvironment.prod, alias="APP_ENV")
    app_type: AppType = Field(default=AppType.api, alias="APP_TYPE")
    app_name: str = Field(default="payment-processing-service", alias="APP_NAME")
    outbox_poll_interval_seconds: int = Field(default=1, alias="OUTBOX_POLL_INTERVAL_SECONDS")
    webhook_timeout_seconds: int = Field(default=5, alias="WEBHOOK_TIMEOUT_SECONDS")

    db: DatabaseSettings = DatabaseSettings()
    log: LogSettings = Field(default_factory=LogSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    rabbitmq: RabbitSettings = Field(default_factory=RabbitSettings)

    app_version: str = Field(default="0.1.0", alias="APP_VERSION")


settings = ApplicationSettings()
