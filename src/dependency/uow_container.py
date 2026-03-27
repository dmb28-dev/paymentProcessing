from fastapi import Request

from src.modules.payment.infrastructure.uow import PaymentUow


async def get_uow(request: Request):
    session_factory = request.app.state.core_container.session_factory
    async with PaymentUow(session_factory) as uow:
        yield uow
