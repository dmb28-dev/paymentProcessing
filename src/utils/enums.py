from enum import StrEnum


class ApplicationEnvironment(StrEnum):
    local = "local"
    dev = "dev"
    prod = "prod"


class AppType(StrEnum):
    api = "api"
    internal = "internal/api"
    srv = "srv"


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


class UserRole(StrEnum):
    defualt = "ROLE.DEFUALT"
    admin = "ROLE.ADMIN"
