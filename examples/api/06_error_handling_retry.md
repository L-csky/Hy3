<p align="left">
  English&nbsp;|&nbsp;<a href="./06_error_handling_retry_CN.md">Chinese</a>
</p>

# 06 | Error Handling, Retries, and Backoff

Complete program: [06_error_handling_retry.py](06_error_handling_retry.py)

## Error Classification

| Type | Retry? | Reason |
| --- | --- | --- |
| Timeout or connection failure | Yes, a limited number | Often a transient network problem |
| 408, 409, 429 | Yes | Timeout, conflict, or rate limiting may recover |
| 500, 502, 503, 504 | Yes | Transient service failure |
| 400 | No | Retrying the same invalid request cannot succeed |
| 401, 403 | No | Credentials or permissions require intervention |
| Other unknown exception | No | Avoid hiding application defects |

The example sets the SDK's `max_retries` to 0 so that all retries remain
visible in application code and SDK retries do not multiply application
retries.

## Wait Strategy

When a response contains `Retry-After`, the code supports both seconds and HTTP
date formats and waits as instructed. Otherwise it uses:

```text
min(base * 2^attempt + random(0, 1) * base, cap)
```

Jitter prevents multiple clients from retrying at the same instant. In addition
to `max_attempts=4`, the program has a `max_total_wait=60` budget. If
`Retry-After` exceeds the remaining budget, it stops and returns control to the
caller instead of retrying early.

```python
response = call_with_retry(
    lambda: client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": "Explain exponential backoff."}],
    )
)
```

## Example Output

```text
attempt 1 failed with RateLimitError; retrying in 2.00s
attempt 2 failed with APIConnectionError; retrying in 2.37s
assistant: Exponential backoff increases the delay after consecutive failures.
```

Production systems should also record redacted request IDs, status codes,
attempt counts, and latency. Consider idempotency before retrying operations
with side effects.

Run with `python 06_error_handling_retry.py`.
