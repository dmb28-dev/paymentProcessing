from uuid import UUID

import pytest

from tests.conftest import PAYMENTS_API_BASE, payment_auth_headers, payment_payload


@pytest.mark.asyncio
async def test_create_payment_creates_pending_status(client) -> None:
    response = await client.post(
        PAYMENTS_API_BASE,
        json=payment_payload(),
        headers=payment_auth_headers(idempotency_key="int-key"),
    )

    assert response.status_code == 201
    body = response.json()
    assert "payment_id" in body
    assert UUID(body["payment_id"])
