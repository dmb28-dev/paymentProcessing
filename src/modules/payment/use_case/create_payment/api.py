from fastapi import Depends, Response, status

from src.dependency.uow_container import get_uow
from src.modules import payment_router as router
from src.modules.payment.infrastructure.dto import (
    CreatePaymentInput,
    CreatePaymentRequest,
    CreatePaymentResponse,
)
from src.modules.payment.infrastructure.uow import PaymentUow
from src.modules.payment.use_case.create_payment.impl import invoke as create_payment_invoke
from src.modules.utils.validate_dependencies import require_idempotency_key


@router.post("", response_model=CreatePaymentResponse, status_code=status.HTTP_202_ACCEPTED)
async def invoke(
    payload: CreatePaymentRequest,
    response: Response,
    idempotency_key: str = Depends(require_idempotency_key),
    uow: PaymentUow = Depends(get_uow),
) -> CreatePaymentResponse:
    dto = await create_payment_invoke(
        data=CreatePaymentInput(
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            metadata=payload.metadata,
            webhook_url=str(payload.webhook_url),
            idempotency_key=idempotency_key,
        ),
        uow=uow,
    )
    response.status_code = status.HTTP_202_ACCEPTED
    return dto
