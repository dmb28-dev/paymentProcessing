from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from src.core.config import get_settings
from src.utils.constants import (
    DLQ_EXCHANGE,
    DLQ_QUEUE,
    DLQ_ROUTING_KEY,
    PAYMENTS_EXCHANGE,
    PAYMENTS_QUEUE,
    PAYMENTS_ROUTING_KEY,
)

settings = get_settings()
broker = RabbitBroker(settings.rabbitmq_url)

payments_exchange = RabbitExchange(
    PAYMENTS_EXCHANGE,
    type=ExchangeType.DIRECT,
    durable=True,
    declare=True,
)
payments_queue = RabbitQueue(
    PAYMENTS_QUEUE,
    routing_key=PAYMENTS_ROUTING_KEY,
    durable=True,
    arguments={
        "x-dead-letter-exchange": DLQ_EXCHANGE,
        "x-dead-letter-routing-key": DLQ_ROUTING_KEY,
    },
)

dlq_exchange = RabbitExchange(
    DLQ_EXCHANGE,
    type=ExchangeType.DIRECT,
    durable=True,
    declare=True,
)
dlq_queue = RabbitQueue(DLQ_QUEUE, routing_key=DLQ_ROUTING_KEY, durable=True)
