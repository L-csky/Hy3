"""Explicit bounded retries for timeout, connection, throttling, and 5xx errors."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    PermissionDeniedError,
)

from common import configure_utf8_output, load_settings

RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """Parse Retry-After as seconds or an HTTP date."""

    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        return max(0.0, (retry_at - current).total_seconds())


def retry_delay(
    attempt: int,
    *,
    retry_after: str | None = None,
    base: float = 1.0,
    cap: float = 30.0,
    jitter: Callable[[], float] = random.random,
) -> float:
    """Honor Retry-After; otherwise use capped exponential backoff + jitter."""

    server_delay = parse_retry_after(retry_after)
    if server_delay is not None:
        return server_delay
    return min(base * (2**attempt) + jitter() * base, cap)


def retryable(error: Exception) -> bool:
    if isinstance(error, (APIConnectionError, APITimeoutError)):
        return True
    return (
        isinstance(error, APIStatusError)
        and error.status_code in RETRYABLE_STATUS_CODES
    )


def call_with_retry(
    operation: Callable[[], Any],
    *,
    max_attempts: int = 4,
    max_total_wait: float = 60.0,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    """Run an API operation with finite retries and a total wait budget."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    waited = 0.0
    for attempt in range(max_attempts):
        try:
            return operation()
        except (AuthenticationError, PermissionDeniedError, BadRequestError):
            raise  # Retrying invalid credentials or invalid input will not help.
        except Exception as error:
            final_attempt = attempt + 1 >= max_attempts
            if final_attempt or not retryable(error):
                raise
            response = getattr(error, "response", None)
            retry_after = (
                None if response is None else response.headers.get("Retry-After")
            )
            delay = retry_delay(attempt, retry_after=retry_after)
            if waited + delay > max_total_wait:
                raise RuntimeError("Retry wait budget exhausted") from error
            print(
                f"attempt {attempt + 1} failed with {type(error).__name__}; "
                f"retrying in {delay:.2f}s"
            )
            sleep(delay)
            waited += delay
    raise AssertionError("unreachable")


def main() -> None:
    configure_utf8_output()
    settings = load_settings()
    # Disable SDK retries here so this example owns and explains every retry.
    client = OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
        max_retries=0,
    )

    response = call_with_retry(
        lambda: client.chat.completions.create(
            model=settings.model,
            messages=[{"role": "user", "content": "请用一句话解释指数退避。"}],
            temperature=0.9,
            top_p=1.0,
            max_tokens=128,
        )
    )
    print(f"assistant: {response.choices[0].message.content}")


if __name__ == "__main__":
    main()
