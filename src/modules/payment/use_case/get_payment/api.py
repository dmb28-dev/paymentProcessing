from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from src.dependency.container import Container
from src.modules import payment_router as router
from src.modules.payment.infrastructure.dto import PaymentResponse
from src.modules.payment.use_case.get_payment.impl import GetPaymentUseCase


@router.get("/{payment_id}", response_model=PaymentResponse)
@inject
async def invoke(
    payment_id: UUID,
    use_case: Annotated[
        GetPaymentUseCase,
        Depends(Provide[Container.get_payment_use_case]),
    ],
) -> PaymentResponse:
    return await use_case.invoke(payment_id)
