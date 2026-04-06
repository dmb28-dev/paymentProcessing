from dependency_injector import providers
from dependency_injector.containers import copy

from src.core.containers import CoreContainer
from src.modules.payment.infrastructure.uow import PaymentUow


@copy(CoreContainer)
class UowContainer(CoreContainer):
    payment_uow = providers.Factory(
        PaymentUow,
        session_factory=CoreContainer.db.provided.session_factory,
    )
