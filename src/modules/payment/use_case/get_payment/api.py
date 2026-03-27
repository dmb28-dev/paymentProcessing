from uuid import UUID

from fastapi import Depends

from src.dependency.uow_container import get_uow
from src.modules import payment_router as router
from src.modules.payment.infrastructure.dto import PaymentResponse
from src.modules.payment.infrastructure.uow import PaymentUow
from src.modules.payment.use_case.get_payment.impl import invoke as get_payment_invoke


@router.get("/{payment_id}", response_model=PaymentResponse)
async def invoke(
    payment_id: UUID,
    uow: PaymentUow = Depends(get_uow),
) -> PaymentResponse:
    return await get_payment_invoke(payment_id=payment_id, uow=uow)
