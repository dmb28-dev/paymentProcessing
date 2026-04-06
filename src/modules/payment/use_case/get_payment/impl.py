from uuid import UUID

from fastapi import HTTPException, status
from pymfdata.common.usecase import BaseUseCase
from pymfdata.rdb.transaction import async_transactional

from src.modules.payment.domain.aggregate.model import Payment
from src.modules.payment.infrastructure.dto import PaymentResponse
from src.modules.payment.infrastructure.uow import PaymentUow


class GetPaymentUseCase(BaseUseCase[PaymentUow]):
    def __init__(self, uow: PaymentUow) -> None:
        self._uow = uow

    @async_transactional(read_only=True)
    async def invoke(self, payment_id: UUID) -> PaymentResponse:
        payment = await self.uow.payments.get_by_id(payment_id=payment_id)
        if payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="payment not found")
        return _map_payment_to_response(payment=payment)


def _map_payment_to_response(*, payment: Payment) -> PaymentResponse:
    return PaymentResponse(
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        metadata=payment.metadata_json,
        status=payment.status,
        idempotency_key=payment.idempotency_key,
        webhook_url=payment.webhook_url,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )
