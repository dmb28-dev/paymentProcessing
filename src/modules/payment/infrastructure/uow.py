from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.persistance.outbox.repository import OutboxRepository
from src.persistance.payment.repository import PaymentRepository


class PaymentUow:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None
        self.payments: PaymentRepository | None = None
        self.outbox: OutboxRepository | None = None

    async def __aenter__(self) -> "PaymentUow":
        self.session = self.session_factory()
        self.payments = PaymentRepository(self.session)
        self.outbox = OutboxRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return
        if exc is None:
            await self.session.commit()
        else:
            await self.session.rollback()
        await self.session.close()
