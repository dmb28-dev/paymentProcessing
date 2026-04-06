from pydantic import BaseModel, ConfigDict, Field


class ServerSettings(BaseModel):

    host: str = Field(default="0.0.0.0", alias="SERVER_HOST")
    port: int = Field(default=8000, alias="SERVER_PORT")
