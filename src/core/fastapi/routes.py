from fastapi import FastAPI

from src.modules import payment_router
from src.modules.payment.use_case.create_payment import api as _create_payment_api
from src.modules.payment.use_case.get_payment import api as _get_payment_api


def include_routers(app: FastAPI) -> None:
    _ = (_create_payment_api, _get_payment_api)
    app.include_router(payment_router)
