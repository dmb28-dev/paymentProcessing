from pydantic import BaseModel, ConfigDict, Field


class LogSettings(BaseModel):

    level: str = Field(default="INFO", alias="LOG_LEVEL")
