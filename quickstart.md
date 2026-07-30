# Hy3 API Quickstart

> Make the first request in five minutes and learn chat, streaming, tools,
> reasoning, and reliable retries in thirty minutes. 中文版：
> [quickstart_CN.md](quickstart_CN.md).

Hy3 exposes an OpenAI-compatible Chat Completions API. Use Tencent Cloud
TokenHub (`https://tokenhub.tencentmaas.com/v1`, model `hy3`) or a local
vLLM/SGLang server (`http://127.0.0.1:8000/v1`, key `EMPTY`). The TokenHub
Singapore endpoint is `https://tokenhub-intl.tencentmaas.com/v1`; use the
region where your resource is enabled.

## Five-minute request

```bash
export HY3_API_KEY="replace-with-your-key"
curl https://tokenhub.tencentmaas.com/v1/chat/completions \
  -H "Authorization: Bearer $HY3_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hy3",
    "messages": [{"role": "user", "content": "Introduce Hy3 in one sentence."}],
    "temperature": 0.9,
    "top_p": 1.0,
    "max_tokens": 128
  }'
```

```bash
python -m pip install "openai>=1.30,<3"
```

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://tokenhub.tencentmaas.com/v1",
    api_key=os.environ["HY3_API_KEY"],
    timeout=60.0,
)
response = client.chat.completions.create(
    model="hy3",
    messages=[{"role": "user", "content": "Introduce Hy3 in one sentence."}],
    temperature=0.9,
    top_p=1.0,
    max_tokens=128,
)
print(response.choices[0].message.content)
print("finish_reason:", response.choices[0].finish_reason)
```

For local serving, change the client to:

```python
client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="EMPTY")
```

## Parameters

| Parameter | Meaning |
| --- | --- |
| `temperature` | Sampling randomness; repository recommendation: `0.9`. |
| `top_p` | Nucleus sampling threshold; repository recommendation: `1.0`. |
| `max_tokens` | Maximum generated tokens; reserve more for reasoning. |
| `stop` | String/list that stops generation when matched. |
| `stream` | Return incremental chunks instead of one response. |
| `tools` | JSON Schema functions; the application executes them. |
| `tool_choice` | Tool selection policy; TokenHub tool flows use `auto`. |

`finish_reason="length"` means the response was truncated.

## Reasoning mode

TokenHub uses `thinking.type` to enable reasoning and a top-level
`reasoning_effort` to select its depth:

```python
extra_body={
    "thinking": {"type": "enabled"},
    "reasoning_effort": "high",
}
```

The self-hosted repository chat-template convention is:

```python
extra_body={"chat_template_kwargs": {"reasoning_effort": "high"}}
```

Disable TokenHub reasoning with `{"thinking": {"type": "disabled"}}`.
TokenHub supports `low`, `medium`, or `high` after reasoning is enabled.
Self-hosted chat templates use `no_think`, `low`, or `high`; confirm what the
target service version supports.
Provider-specific reasoning can be read with
`getattr(message, "reasoning_content", "")`. In reasoning-plus-tool flows,
preserve the complete assistant message in the next request.

## Limits, retries, and troubleshooting

There is no repository-wide fixed RPM/TPM. TokenHub limits depend on account,
region, and resources; local throughput depends on hardware and gateway policy.
Honor `Retry-After` for 429. Retry timeouts, connections, 429, and selected 5xx
errors with finite backoff and jitter. Never retry invalid credentials,
permissions, or malformed requests.

Check `/v1/models` for 401/404 issues. Ensure the Base URL includes `/v1`.
Iterate all streaming chunks because usage-only chunks may have empty `choices`.
Bound tool loops and validate all tool names and JSON arguments.

Never commit API keys or place them in notebooks, logs, screenshots, or Git
history.

## Complete examples

See [`examples/api/README.md`](examples/api/README.md) for six runnable Python
examples and detailed per-example protocol notes. The
[Chinese quickstart](quickstart_CN.md) contains the complete parameter and
troubleshooting tables.

Official references: [TokenHub API](https://cloud.tencent.com/document/product/1823/130078),
[Hy3 guide](https://cloud.tencent.com/document/product/1823/132252), and
[interleaved reasoning](https://cloud.tencent.com/document/product/1823/130930).
