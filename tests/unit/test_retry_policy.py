from src.adapters.webhook.webhook_client import get_exponential_backoff_delays, is_retryable_status


def test_retry_backoff() -> None:
    assert get_exponential_backoff_delays(attempts=3) == [1, 2, 4]


def test_retryable_statuses() -> None:
    assert is_retryable_status(status_code=429)
    assert is_retryable_status(status_code=503)
    assert not is_retryable_status(status_code=400)
