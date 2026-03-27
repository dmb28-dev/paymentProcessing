import pytest

from tests.conftest import payment_payload


@pytest.mark.asyncio
async def test_create_payment_is_idempotent(client) -> None:  # noqa: ANN001
    headers = {"X-API-Key": "dev-secret-key", "Idempotency-Key": "same-key"}
    first = await client.post("/api/v1/payments", json=payment_payload(), headers=headers)
    second = await client.post("/api/v1/payments", json=payment_payload(), headers=headers)

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["payment_id"] == second.json()["payment_id"]
