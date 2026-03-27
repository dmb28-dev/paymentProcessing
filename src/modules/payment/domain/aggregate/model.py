from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from src.modules.payment.domain.value_objects import Amount, IdempotencyKey, Metadata, WebhookUrl
from src.utils.enums import Currency, OutboxStatus, PaymentStatus


@dataclass(slots=True)
class Payment:
    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata_json: dict[str, Any]
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        amount: Decimal,
        currency: Currency,
        description: str,
        metadata: dict[str, Any],
        webhook_url: str,
        idempotency_key: str,
    ) -> "Payment":
        validated_amount = Amount(amount=amount, currency=currency)
        validated_idempotency_key = IdempotencyKey(value=idempotency_key)
        validated_webhook_url = WebhookUrl(value=webhook_url)
        validated_metadata = Metadata(value=metadata)

        if len(description) > 255:
            raise ValueError("description is too long")

        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            amount=validated_amount.amount,
            currency=validated_amount.currency,
            description=description,
            metadata_json=validated_metadata.value,
            status=PaymentStatus.PENDING,
            idempotency_key=validated_idempotency_key.value,
            webhook_url=validated_webhook_url.value,
            created_at=now,
            processed_at=None,
        )

    def mark_processed(
        self,
        *,
        status: PaymentStatus,
        processed_at: datetime | None = None,
    ) -> None:
        self.status = status
        self.processed_at = processed_at if processed_at is not None else datetime.now(UTC)

    def as_payment_model_kwargs(self) -> dict[str, Any]:
        return {
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "metadata_json": self.metadata_json,
            "status": self.status,
            "idempotency_key": self.idempotency_key,
            "webhook_url": self.webhook_url,
            "processed_at": self.processed_at,
        }


@dataclass(slots=True)
class OutboxEvent:
    aggregate_type: str
    aggregate_id: UUID
    event_type: str
    payload: dict[str, Any]
    status: OutboxStatus
    attempts: int
    next_retry_at: datetime

    @classmethod
    def payment_created(cls, *, payment_id: UUID) -> "OutboxEvent":
        return cls(
            aggregate_type="payment",
            aggregate_id=payment_id,
            event_type="payment_created",
            payload={"payment_id": str(payment_id)},
            status=OutboxStatus.PENDING,
            attempts=0,
            next_retry_at=datetime.now(UTC),
        )

