from typing import Any

from src.adapters.rabbitmq.broker import broker, payments_queue


async def publish_payment_created(*, payload: dict[str, Any]) -> None:
    await broker.publish(
        payload,
        queue=payments_queue,
        mandatory=True,
    )
