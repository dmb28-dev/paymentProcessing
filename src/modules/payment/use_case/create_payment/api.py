from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Response, status

from src.dependency.container import Container
from src.dependency.parse_token import TokenVerify, UserToken
from src.modules import payment_router as router
from src.modules.payment.infrastructure.dto import (
    CreatePaymentInput,
    CreatePaymentRequest,
    CreatePaymentResponse,
)
from src.modules.payment.use_case.create_payment.impl import CreatePaymentUseCase
from src.modules.utils.validate_dependencies import require_idempotency_key


@router.post("", response_model=CreatePaymentResponse, status_code=status.HTTP_201_CREATED)
@inject
async def invoke(
    payload: CreatePaymentRequest,
    use_case: Annotated[
        CreatePaymentUseCase,
        Depends(Provide[Container.create_payment_use_case]),
    ],
    idempotency_key: str = Depends(require_idempotency_key),
    user_info: UserToken = Depends(TokenVerify()),
) -> CreatePaymentResponse:
    dto = await use_case.invoke(
        CreatePaymentInput(
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            metadata=payload.metadata,
            webhook_url=str(payload.webhook_url),
            idempotency_key=idempotency_key,
        ),
    )
    return dto
