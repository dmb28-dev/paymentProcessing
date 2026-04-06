from pydantic import BaseModel, ConfigDict, Field


class RabbitSettings(BaseModel):

    url: str = Field(default="amqp://guest:guest@localhost:5672/", alias="RABBITMQ_URL")
