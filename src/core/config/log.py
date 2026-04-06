from pydantic import BaseModel, ConfigDict, Field


class LogSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    level: str = Field(default="INFO", alias="LOG_LEVEL")
