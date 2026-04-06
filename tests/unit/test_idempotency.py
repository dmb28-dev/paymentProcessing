import pytest

from tests.conftest import PAYMENTS_API_BASE, payment_payload


@pytest.mark.asyncio
async def test_create_payment_is_idempotent(client) -> None:
    headers = {"X-API-Key": "dev-secret-key", "Idempotency-Key": "same-key"}
    first = await client.post(PAYMENTS_API_BASE, json=payment_payload(), headers=headers)
    second = await client.post(PAYMENTS_API_BASE, json=payment_payload(), headers=headers)

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["payment_id"] == second.json()["payment_id"]
