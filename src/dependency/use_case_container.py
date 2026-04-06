from dependency_injector.containers import copy
from dependency_injector.providers import Factory
from fastapi import Request

from src.dependency.uow_container import UowContainer
from src.modules.payment.use_case.create_payment.impl import CreatePaymentUseCase
from src.modules.payment.use_case.get_payment.impl import GetPaymentUseCase


@copy(UowContainer)
class UseCaseContainer(UowContainer):
    create_payment_use_case = Factory(
        CreatePaymentUseCase,
        uow=UowContainer.payment_uow,
    )
    get_payment_use_case = Factory(
        GetPaymentUseCase,
        uow=UowContainer.payment_uow,
    )
