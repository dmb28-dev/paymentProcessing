from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.payment.domain.aggregate.model import OutboxEvent, Payment
from src.persistance.outbox.entity import OutboxModel
from src.persistance.payment.entity import PaymentModel
from src.utils.enums import OutboxStatus


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, *, payment_id: UUID) -> PaymentModel | None:
        result = await self.session.execute(select(PaymentModel).where(PaymentModel.id == payment_id))
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, *, idempotency_key: str) -> PaymentModel | None:
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def add(self, *, payment: PaymentModel | Payment) -> PaymentModel:
        if isinstance(payment, Payment):
            payment = PaymentModel(**payment.as_payment_model_kwargs())
        self.session.add(payment)
        await self.session.flush()
        return payment
