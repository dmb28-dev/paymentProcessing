from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import urlparse

from src.utils.enums import Currency


@dataclass(frozen=True, slots=True)
class Amount:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be positive")


@dataclass(frozen=True, slots=True)
class IdempotencyKey:
    value: str

    def __post_init__(self) -> None:
        normalized = (self.value or "").strip()
        if not normalized:
            raise ValueError("idempotency_key is empty")
        if len(normalized) > 128:
            raise ValueError("idempotency_key is too long")


@dataclass(frozen=True, slots=True)
class WebhookUrl:
    value: str

    def __post_init__(self) -> None:
        url = (self.value or "").strip()
        if not url:
            raise ValueError("webhook_url is empty")
        if len(url) > 1024:
            raise ValueError("webhook_url is too long")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("webhook_url must use http(s)")


@dataclass(frozen=True, slots=True)
class Metadata:
    value: dict[str, Any]

    def __post_init__(self) -> None:
        if self.value is None:
            object.__setattr__(self, "value", {})
        if not isinstance(self.value, dict):
            raise ValueError("metadata must be a dict")


def now_utc() -> datetime:
    return datetime.now(UTC)

