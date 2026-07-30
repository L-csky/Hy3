<p align="left">
  English&nbsp;|&nbsp;<a href="./02_streaming_CN.md">Chinese</a>
</p>

# 02 | Streaming Requests and Per-Chunk Parsing

Complete program: [02_streaming.py](02_streaming.py)

## Request and Parsing

A streaming request sets `stream=True` and returns an iterable event stream,
not one complete response. A chunk may contain only a role, a small content
delta, a reasoning delta, a finish reason, or usage. Do not assume that every
chunk contains a choice or content.

```python
stream = client.chat.completions.create(
    model=settings.model,
    messages=[{"role": "user", "content": "Explain streaming output."}],
    stream=True,
    stream_options={"include_usage": True},
)
parts = []
for chunk in stream:
    if not chunk.choices:  # The final usage-only chunk may enter here.
        continue
    delta = chunk.choices[0].delta
    if delta.content:
        parts.append(delta.content)
        print(delta.content, end="", flush=True)
full_text = "".join(parts)
```

The program accumulates `reasoning_content` separately but does not print
complete reasoning by default. Tool-call arguments can also span multiple
chunks. Production code must accumulate them by tool-call index or ID instead
of calling `json.loads` on an individual fragment.

## Example Output

```text
assistant: Streaming lets users see content before the complete answer...

=== Aggregated result ===
content_chars: 168
reasoning_chars: 0
finish_reason: stop
total_tokens: 102
```

If the service does not implement `stream_options.include_usage`, the script
reports that usage is missing while still parsing the content normally.

Run with `python 02_streaming.py`.
