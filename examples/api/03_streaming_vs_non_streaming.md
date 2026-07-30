<p align="left">
  English&nbsp;|&nbsp;<a href="./03_streaming_vs_non_streaming_CN.md">Chinese</a>
</p>

# 03 | Streaming vs. Non-Streaming Latency

Complete program:
[03_streaming_vs_non_streaming.py](03_streaming_vs_non_streaming.py)

## Metric Definitions

- **Non-streaming total latency**: Time from sending the request until the
  complete response is returned.
- **Streaming TTFT**: Time from sending the request until the first non-empty,
  visible `delta.content`. This is not TCP time to first byte or a chunk that
  contains only a role or reasoning.
- **Streaming total latency**: Time from sending the request until stream
  iteration finishes.

The measurement uses the monotonic high-resolution `time.perf_counter()` clock:

```python
started = perf_counter()
stream = client.chat.completions.create(..., stream=True)
first_content_at = None
for chunk in stream:
    content = chunk.choices[0].delta.content if chunk.choices else None
    if content and first_content_at is None:
        first_content_at = perf_counter()
total = perf_counter() - started
ttft = first_content_at - started
```

## Correct Interpretation

One script run demonstrates the measurement method; it is not a benchmark.
Requests may generate different output lengths and are affected by cold starts,
queueing, networks, caches, and service load. A formal comparison should warm
up the service, fix region and parameters, alternate multiple runs, and report
the median and P95.

```text
=== Latency comparison (one sample, not a benchmark) ===
non-streaming total: 2.841s
streaming TTFT: 0.612s
streaming total: 3.104s
non-streaming chars: 174
streaming chars: 181
Run multiple warm samples before drawing performance conclusions.
```

Streaming usually provides earlier visible output; it does not guarantee lower
total latency. Run with `python 03_streaming_vs_non_streaming.py`.
