import asyncio
from datetime import UTC, datetime
from uuid import UUID

from faststream.rabbit import RabbitMessage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.adapters.webhook.webhook_client import send_webhook_with_retry
from src.adapters.rabbitmq.broker import broker, dlq_exchange, dlq_queue, payments_exchange, payments_queue
from src.adapters.rabbitmq.publisher import publish_payment_created
from src.clients.payment_gateway_client import emulate_payment_gateway
from src.core.config import get_settings
from src.modules.payment.infrastructure.uow import PaymentUow
from src.utils.constants import DLQ_QUEUE, MAX_RETRIES
from src.utils.enums import PaymentStatus

from loguru import logger


async def dispatch_outbox_forever() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Ensure exchanges/queues are declared before first publish.
    await broker.declare_exchange(payments_exchange)
    await broker.declare_queue(payments_queue)
    await broker.declare_exchange(dlq_exchange)
    await broker.declare_queue(dlq_queue)
    while True:
        async with PaymentUow(session_factory) as uow:
            if uow.outbox is None:
                await asyncio.sleep(settings.outbox_poll_interval_seconds)
                continue
            events = await uow.outbox.get_pending_batch(limit=100)
            if events:
                logger.bind(count=len(events)).info("outbox batch loaded")
            for event in events:
                try:
                    await publish_payment_created(payload=event.payload)
                    uow.outbox.mark_published(event=event)
                except Exception as error:  # noqa: BLE001
                    error_message = f"{type(error).__name__}: {error}"
                    uow.outbox.mark_retry(event=event, error_message=error_message)
                    logger.bind(
                        outbox_id=str(event.id),
                        aggregate_id=str(event.aggregate_id),
                        attempts=event.attempts,
                        error_message=error_message,
                        status_type=type(event.status).__name__,
                        status=str(event.status),
                        payload=event.payload,
                    ).exception("outbox publish failed")
        await asyncio.sleep(settings.outbox_poll_interval_seconds)


@broker.subscriber(payments_queue)
async def consume_payment_created(payload: dict[str, str], msg: RabbitMessage) -> None:
    settings = get_settings()
    payment_id = payload.get("payment_id")
    if payment_id is None:
        logger.bind(payload=payload).warning("message missing payment_id, sending to dlq")
        try:
            confirmation = await broker.publish(payload, queue=DLQ_QUEUE, persist=True)
            logger.bind(confirmation=str(confirmation), payload=payload).error("published to dlq")
        except Exception:  # noqa: BLE001
            logger.bind(payload=payload).exception("dlq publish failed")
        await msg.ack()
        return

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with PaymentUow(session_factory) as uow:
        if uow.payments is None:
            await msg.nack(requeue=True)
            return

        payment = await uow.payments.get_by_id(payment_id=UUID(payment_id))
        if payment is None:
            logger.bind(payment_id=payment_id).warning("payment not found, sending to dlq")
            try:
                confirmation = await broker.publish(payload, queue=DLQ_QUEUE, persist=True)
                logger.bind(confirmation=str(confirmation), payload=payload).error("published to dlq")
            except Exception:  # noqa: BLE001
                logger.bind(payload=payload).exception("dlq publish failed")
            await msg.ack()
            return
        if payment.status != PaymentStatus.PENDING:
            logger.bind(payment_id=str(payment.id), status=str(payment.status)).info(
                "payment already processed, ack"
            )
            await msg.ack()
            return

        payment.status = await emulate_payment_gateway()
        payment.processed_at = datetime.now(UTC)
        logger.bind(
            payment_id=str(payment.id),
            status=str(payment.status),
            webhook_url=payment.webhook_url,
        ).info("payment processed, sending webhook")
        is_sent = await send_webhook_with_retry(
            webhook_url=payment.webhook_url,
            payload={
                "payment_id": str(payment.id),
                "status": payment.status.value if hasattr(payment.status, "value") else str(payment.status),
            },
            timeout_seconds=settings.webhook_timeout_seconds,
            attempts=MAX_RETRIES,
        )
        if is_sent:
            logger.bind(payment_id=str(payment.id)).info("webhook sent, ack")
            await msg.ack()
            return
        logger.bind(payment_id=str(payment.id)).error("webhook failed, sending to dlq")
        try:
            confirmation = await broker.publish(payload, queue=DLQ_QUEUE, persist=True)
            logger.bind(confirmation=str(confirmation), payload=payload).error("published to dlq")
        except Exception:  # noqa: BLE001
            logger.bind(payload=payload).exception("dlq publish failed")
        await msg.ack()


async def run_consumer() -> None:
    await broker.connect()
    await broker.start()
    await dispatch_outbox_forever()
