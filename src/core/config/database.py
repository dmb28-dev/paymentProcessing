from pydantic import BaseModel, ConfigDict, Field, PostgresDsn, field_validator


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    database_url: PostgresDsn | str = Field(
        default="postgresql+asyncpg://payments:payments@localhost:5432/payments",
        alias="DATABASE_URL",
    )

    @field_validator("database_url", mode="after")
    @classmethod
    def ensure_asyncpg_driver(cls, value: object) -> str:
        s = str(value)
        if "asyncpg" in s:
            return s
        return s.replace("postgresql", "postgresql+asyncpg", 1)
