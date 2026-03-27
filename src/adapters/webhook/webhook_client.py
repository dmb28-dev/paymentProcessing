import asyncio
from http import HTTPStatus
from typing import Any

import httpx

from src.utils.constants import MAX_RETRIES


def get_exponential_backoff_delays(*, attempts: int) -> list[int]:
    return [2**index for index in range(attempts)]


def is_retryable_status(*, status_code: int) -> bool:
    return status_code in {
        HTTPStatus.REQUEST_TIMEOUT,
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }


async def send_webhook_with_retry(
    *,
    webhook_url: str,
    payload: dict[str, Any],
    timeout_seconds: int,
    attempts: int = MAX_RETRIES,
) -> bool:
    delays = get_exponential_backoff_delays(attempts=attempts)
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        for attempt, delay in enumerate(delays, start=1):
            try:
                response = await client.post(webhook_url, json=payload)
                if 200 <= response.status_code < 300:
                    return True
                if not is_retryable_status(status_code=response.status_code):
                    return False
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
                pass
            if attempt < attempts:
                await asyncio.sleep(delay)
    return False
