import pytest

from tests.conftest import PAYMENTS_API_BASE, payment_auth_headers, payment_payload


@pytest.mark.asyncio
async def test_create_and_get_payment_smoke(client) -> None:
    create_response = await client.post(
        PAYMENTS_API_BASE,
        json=payment_payload(),
        headers=payment_auth_headers(idempotency_key="smoke-key"),
    )
    assert create_response.status_code == 201
    payment_id = create_response.json()["payment_id"]

    get_response = await client.get(
        f"{PAYMENTS_API_BASE}/{payment_id}",
        headers=payment_auth_headers(),
    )
    assert get_response.status_code == 200
    assert get_response.json()["payment_id"] == payment_id
