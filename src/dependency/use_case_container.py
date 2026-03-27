from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.payment.infrastructure.dto import CreatePaymentInput, PaymentResponse
from src.modules.payment.use_case.create_payment.impl import (
    invoke as create_payment_invoke,
)
from src.modules.payment.use_case.get_payment.impl import invoke as get_payment_invoke
from src.modules.payment.infrastructure.uow import PaymentUow


@dataclass(slots=True, frozen=True)
class UseCaseContainer:
    session_factory: async_sessionmaker[AsyncSession]

    async def create_payment(self, *, data: CreatePaymentInput) -> PaymentResponse:
        async with PaymentUow(self.session_factory) as uow:
            return await create_payment_invoke(data=data, uow=uow)

    async def create_payment_use_case(
        self,
        *,
        data: CreatePaymentInput,
    ) -> PaymentResponse:
        return await self.create_payment(data=data)

    async def get_payment(self, *, payment_id: UUID) -> PaymentResponse:
        async with PaymentUow(self.session_factory) as uow:
            return await get_payment_invoke(payment_id=payment_id, uow=uow)

    async def get_payment_use_case(self, *, payment_id: UUID) -> PaymentResponse:
        return await self.get_payment(payment_id=payment_id)


def invoke(session_factory: async_sessionmaker[AsyncSession]) -> UseCaseContainer:
    return UseCaseContainer(session_factory=session_factory)


def get_use_case_container(request: Request) -> UseCaseContainer:
    session_factory = request.app.state.core_container.session_factory
    return invoke(session_factory=session_factory)
