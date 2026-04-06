from pymfdata.common.usecase import BaseUseCase
from pymfdata.rdb.transaction import async_transactional

from src.modules.payment.domain.aggregate.model import OutboxEvent, Payment
from src.modules.payment.infrastructure.dto import CreatePaymentInput, CreatePaymentResponse
from src.modules.payment.infrastructure.uow import PaymentUow


class CreatePaymentUseCase(BaseUseCase[PaymentUow]):
    def __init__(self, uow: PaymentUow) -> None:
        self._uow = uow

    @async_transactional()
    async def invoke(self, data: CreatePaymentInput) -> CreatePaymentResponse:
        
        existing_payment = await self.uow.payments.get_by_idempotency_key(idempotency_key=data.idempotency_key)
        if existing_payment is not None:
            return CreatePaymentResponse(payment_id=existing_payment.id)

        payment = Payment.create(
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            metadata=data.metadata,
            idempotency_key=data.idempotency_key,
            webhook_url=data.webhook_url,
        )
        saved_payment = await self.uow.payments.add(payment=payment)
        await self.uow.outbox.add(event=OutboxEvent.payment_created(payment_id=saved_payment.id))
        return CreatePaymentResponse(payment_id=saved_payment.id)
