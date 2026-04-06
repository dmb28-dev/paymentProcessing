from pydantic import BaseModel, ConfigDict, Field, PostgresDsn, field_validator

from src.core.config.base import BaseSettings

class DatabaseSettings(BaseSettings):
    database_url: PostgresDsn | str = Field(...,alias="DATABASE_URL",)

    @field_validator("database_url", mode="after")
    @classmethod
    def ensure_asyncpg_driver(cls, value: object) -> str:
        s = str(value)
        if "asyncpg" in s:
            return s
        return s.replace("postgresql", "postgresql+asyncpg", 1)
