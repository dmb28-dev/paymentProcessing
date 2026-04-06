from pydantic import BaseModel, ConfigDict, Field


class ClientApi(BaseModel):
    model_config = ConfigDict(extra="ignore")

    api_key: str = Field(default="dev-secret-key", alias="API_KEY")
