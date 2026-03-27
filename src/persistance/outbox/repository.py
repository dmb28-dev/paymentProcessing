from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.payment.domain.aggregate.model import OutboxEvent
from src.persistance.outbox.entity import OutboxModel
from src.utils.enums import OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, *, event: OutboxModel | OutboxEvent) -> OutboxModel:
        if isinstance(event, OutboxEvent):
            event = OutboxModel(
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                event_type=event.event_type,
                payload=event.payload,
                status=event.status,
                attempts=event.attempts,
                next_retry_at=event.next_retry_at,
            )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_pending_batch(self, *, limit: int) -> list[OutboxModel]:
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(OutboxModel)
            .where(OutboxModel.status == OutboxStatus.PENDING, OutboxModel.next_retry_at <= now)
            .order_by(OutboxModel.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    def mark_published(self, *, event: OutboxModel) -> None:
        event.status = OutboxStatus.PUBLISHED
        event.published_at = datetime.now(UTC)
        event.error_message = None

    def mark_retry(self, *, event: OutboxModel, error_message: str) -> None:
        event.attempts += 1
        event.error_message = error_message
        event.next_retry_at = datetime.now(UTC) + timedelta(seconds=2 ** (event.attempts - 1))
        if event.attempts >= 3:
            event.status = OutboxStatus.FAILED
