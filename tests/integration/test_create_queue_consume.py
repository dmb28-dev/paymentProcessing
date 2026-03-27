import pytest

from tests.conftest import payment_payload


@pytest.mark.asyncio
async def test_create_payment_creates_pending_status(client) -> None:  # noqa: ANN001
    headers = {"X-API-Key": "dev-secret-key", "Idempotency-Key": "int-key"}
    response = await client.post("/api/v1/payments", json=payment_payload(), headers=headers)

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert body["idempotency_key"] == "int-key"
