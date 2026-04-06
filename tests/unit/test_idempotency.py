import pytest

from tests.conftest import PAYMENTS_API_BASE, payment_auth_headers, payment_payload


@pytest.mark.asyncio
async def test_create_payment_is_idempotent(client) -> None:
    headers = payment_auth_headers(idempotency_key="same-key")
    first = await client.post(PAYMENTS_API_BASE, json=payment_payload(), headers=headers)
    second = await client.post(PAYMENTS_API_BASE, json=payment_payload(), headers=headers)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["payment_id"] == second.json()["payment_id"]
