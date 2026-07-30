<p align="left">
  English&nbsp;|&nbsp;<a href="./quickstart_CN.md">Chinese</a>
</p>

# Hy3 API Quickstart

This guide helps developers make their first Hy3 API request in about five
minutes and learn chat, streaming, tool calling, reasoning modes, and reliable
retries in about thirty minutes.

Hy3 provides an OpenAI-compatible Chat Completions API with two API access
modes:

- **TokenHub hosted API**: Create an API key and enable a service without
  deploying the model yourself.
- **Self-hosted API**: Follow the [README](README.md#deployment) to deploy Hy3
  with vLLM or SGLang, then call the OpenAI-compatible API exposed by that
  service.

This guide covers API usage for both services. It does not cover model
downloads, GPU planning, or server deployment.

## 1. Basic Information

| Item | TokenHub Guangzhou | TokenHub Singapore | Self-hosted default |
| --- | --- | --- | --- |
| Base URL | `https://tokenhub.tencentmaas.com/v1` | `https://tokenhub-intl.tencentmaas.com/v1` | `http://127.0.0.1:8000/v1` |
| Chat endpoint | `/chat/completions` | `/chat/completions` | `/chat/completions` |
| API key | Created in the TokenHub console | Created in the TokenHub console | Usually `EMPTY` |
| Model | `hy3` or a service ID | `hy3` or a service ID | Matches `--served-model-name` |
| Protocol | OpenAI Chat Completions | OpenAI Chat Completions | OpenAI-compatible API |

TokenHub does not support cross-region requests. The API key, service resource,
and Base URL must belong to the same region. For a custom online inference
service, use the service ID shown in the console, such as `ep-xxxxxxxx`.

Hy3 supports a model context length of up to 256K tokens. The usable context
also depends on service configuration, input and output budgets, concurrency,
and available GPU memory. This repository does not define a fixed RPM or TPM
that applies to every deployment:

- TokenHub limits depend on the account, region, plan, and inference service.
- Self-hosted throughput depends on GPUs, parallelism, gateway settings, queues,
  and context length.
- On HTTP 429, honor `Retry-After`; otherwise use exponential backoff with
  jitter.

## 2. Configure the Environment

Install the OpenAI Python SDK:

```bash
python -m pip install "openai>=1.30,<3"
```

### Linux / macOS

TokenHub Singapore example:

```bash
export HY3_BASE_URL="https://tokenhub-intl.tencentmaas.com/v1"
export HY3_API_KEY="replace-with-your-key"
export HY3_MODEL="hy3"
```

Self-hosted example:

```bash
export HY3_BASE_URL="http://127.0.0.1:8000/v1"
export HY3_API_KEY="EMPTY"
export HY3_MODEL="hy3"
```

### Windows PowerShell

```powershell
$env:HY3_BASE_URL = "https://tokenhub-intl.tencentmaas.com/v1"
$env:HY3_API_KEY = "replace-with-your-key"
$env:HY3_MODEL = "hy3"
```

Never put a real API key in source code, notebooks, screenshots, or Git
history. Revoke and replace a key immediately if it is exposed.

### Connectivity Check

Linux / macOS:

```bash
curl "${HY3_BASE_URL}/models" \
  -H "Authorization: Bearer ${HY3_API_KEY}"
```

Windows PowerShell:

```powershell
curl.exe "$env:HY3_BASE_URL/models" `
  -H "Authorization: Bearer $env:HY3_API_KEY"
```

The model or service ID returned in the list should match `HY3_MODEL`. Some
self-hosted frameworks also expose `/health`, but that route is not part of the
OpenAI protocol and is not available on every service.

## 3. Make a Request in Five Minutes

### curl

Linux / macOS:

```bash
curl "${HY3_BASE_URL}/chat/completions" \
  -H "Authorization: Bearer ${HY3_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @- <<JSON
{
  "model": "${HY3_MODEL}",
  "messages": [
    {"role": "user", "content": "In one sentence, explain how you can help."}
  ],
  "temperature": 0.9,
  "top_p": 1.0,
  "max_tokens": 128,
  "stream": false
}
JSON
```

Windows PowerShell:

```powershell
$body = @{
  model = $env:HY3_MODEL
  messages = @(
    @{ role = "user"; content = "In one sentence, explain how you can help." }
  )
  temperature = 0.9
  top_p = 1.0
  max_tokens = 128
  stream = $false
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri "$env:HY3_BASE_URL/chat/completions" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $env:HY3_API_KEY" } `
  -ContentType "application/json" `
  -Body $body
```

The core response structure is shown below. IDs, content, and token counts vary:

```json
{
  "id": "chatcmpl-REDACTED",
  "object": "chat.completion",
  "model": "hy3",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Example response content..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 24,
    "total_tokens": 42
  }
}
```

### Python OpenAI SDK

```python
import os

from openai import OpenAI

client = OpenAI(
    base_url=os.environ["HY3_BASE_URL"],
    api_key=os.environ["HY3_API_KEY"],
    timeout=60.0,
)

response = client.chat.completions.create(
    model=os.getenv("HY3_MODEL", "hy3"),
    messages=[
        {"role": "user", "content": "In one sentence, explain how you can help."},
    ],
    temperature=0.9,
    top_p=1.0,
    max_tokens=128,
)

choice = response.choices[0]
print(choice.message.content)
print("finish_reason:", choice.finish_reason)
if response.usage:
    print("total_tokens:", response.usage.total_tokens)
```

The service does not automatically preserve multi-turn conversations. The
client must include earlier `user` and `assistant` messages in order in the
next request. See [`01_basic_chat.py`](examples/api/01_basic_chat.py) for a
complete implementation.

## 4. Request Parameters

| Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `model` | string | `hy3` | Model or service ID returned by `/models` |
| `messages` | array | `system/user/assistant/tool` | Conversation history maintained by the client |
| `temperature` | number | `0.9` | Sampling randomness; the repository recommends `0.9` |
| `top_p` | number | `1.0` | Nucleus sampling threshold; avoid aggressively tuning it together with temperature |
| `max_tokens` | integer | `512` | Output limit; reserve a larger budget for reasoning |
| `stop` | string/array | `["Observation:"]` | Stop generation when a sequence is matched |
| `stream` | boolean | `true` | Return incremental chunks instead of waiting for a complete response |
| `stream_options` | object | `{"include_usage": true}` | Include usage in the final streaming chunk |
| `tools` | array | JSON Schema | Define functions that the model can select |
| `tool_choice` | string/object | `auto` | Control whether or how a tool is selected |
| `parallel_tool_calls` | boolean | `false` | Allow the model to request multiple tools at once |
| `response_format` | object | `{"type": "json_object"}` | Constrain output when supported by the target service |

Supported parameters may differ between service versions. Check the target
service documentation and the actual `/models` response before use.

Common `finish_reason` values:

- `stop`: Generation completed normally.
- `length`: The output budget was reached and the answer may be incomplete.
- `tool_calls`: The model requested that the application execute a tool.

## 5. Reasoning Modes

TokenHub and self-hosted services place reasoning settings in different fields:

| Service | Disable reasoning | Enable reasoning |
| --- | --- | --- |
| TokenHub | `{"thinking":{"type":"disabled"}}` | Set `thinking.type=enabled` and depth to `low/medium/high` |
| Self-hosted | `reasoning_effort=no_think` | Set `reasoning_effort=low/high` |

### TokenHub

```python
response = client.chat.completions.create(
    model=os.getenv("HY3_MODEL", "hy3"),
    messages=[
        {"role": "user", "content": "Prove that the square root of 2 is irrational."}
    ],
    max_tokens=16384,
    extra_body={
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
    },
)
```

To disable reasoning:

```python
extra_body = {"thinking": {"type": "disabled"}}
```

### Self-hosted vLLM/SGLang

```python
extra_body = {
    "chat_template_kwargs": {
        "reasoning_effort": "high",
    }
}
```

Self-hosted templates use `no_think`, `low`, or `high`. The server must also
enable the corresponding reasoning parser. Read the provider-specific
`reasoning_content` field defensively:

```python
reasoning = getattr(response.choices[0].message, "reasoning_content", "")
```

When reasoning and tool calling are combined, preserve the complete assistant
message, including `reasoning_content` and `tool_calls`, in the next request.
Do not log complete reasoning that contains sensitive business data. See
[`05_reasoning_mode.py`](examples/api/05_reasoning_mode.py) for a complete
comparison.

## 6. Streaming Responses

With `stream=True`, the SDK returns an iterable event stream. A chunk may
contain only a role, partial content, a reasoning delta, a finish reason, or
usage. Do not assume every chunk contains text:

```python
stream = client.chat.completions.create(
    model=os.getenv("HY3_MODEL", "hy3"),
    messages=[{"role": "user", "content": "Explain streaming responses."}],
    stream=True,
    stream_options={"include_usage": True},
)

parts = []
for chunk in stream:
    if not chunk.choices:
        continue
    content = chunk.choices[0].delta.content
    if content:
        parts.append(content)
        print(content, end="", flush=True)

full_text = "".join(parts)
```

Tool arguments can also span multiple chunks. Production code must accumulate
them by tool-call index or ID before parsing. See
[`02_streaming.py`](examples/api/02_streaming.py) for a complete implementation.

## 7. Tool Calling

Self-hosted services must enable tool parsing first:

- vLLM: Use `--tool-call-parser hy_v3` and
  `--enable-auto-tool-choice`.
- SGLang: Use the Hunyuan tool-parser configuration documented in the
  repository README.

The complete application-side flow is:

1. Define a `tools` JSON Schema.
2. Send a request with `tool_choice="auto"`.
3. Inspect the assistant's `tool_calls`.
4. Validate the tool name against an allowlist and validate its JSON arguments.
5. Execute the tool in the application.
6. Add a `role="tool"` result message with the same `tool_call_id`.
7. Send the complete history again until the model returns a final answer.

Production code must limit tool rounds and enforce tool timeouts, permissions,
and output size. Never use `eval`, `exec`, or a shell to execute model-generated
content directly. See [`04_tool_calling.py`](examples/api/04_tool_calling.py)
for a complete implementation.

## 8. Example Index

| Guide | Script | Demonstrates |
| --- | --- | --- |
| [Basic chat](examples/api/01_basic_chat.md) | [`01_basic_chat.py`](examples/api/01_basic_chat.py) | Single-turn and multi-turn chat, plus usage |
| [Streaming](examples/api/02_streaming.md) | [`02_streaming.py`](examples/api/02_streaming.py) | Per-chunk parsing and aggregation |
| [Latency comparison](examples/api/03_streaming_vs_non_streaming.md) | [`03_streaming_vs_non_streaming.py`](examples/api/03_streaming_vs_non_streaming.py) | Time to first token and total latency |
| [Tool calling](examples/api/04_tool_calling.md) | [`04_tool_calling.py`](examples/api/04_tool_calling.py) | One call and a bounded tool loop |
| [Reasoning modes](examples/api/05_reasoning_mode.md) | [`05_reasoning_mode.py`](examples/api/05_reasoning_mode.py) | `no_think` and `high` comparison |
| [Errors and retries](examples/api/06_error_handling_retry.md) | [`06_error_handling_retry.py`](examples/api/06_error_handling_retry.py) | Error classification and exponential backoff |

Each guide includes the request flow, response parsing, important caveats, and
redacted output examples. See
[`examples/api/README.md`](examples/api/README.md) for installation and run
instructions.

## 9. Troubleshooting

| Symptom | Common cause | Resolution |
| --- | --- | --- |
| HTTP 400 | Invalid parameter type, message order, tool Schema, or unsupported capability | Inspect a redacted request and reduce it field by field; do not retry unchanged |
| HTTP 401 / `401002` | Missing or invalid key, or region mismatch | Match the key and Base URL region, then verify with `/models` |
| HTTP 402 / endpoint inactive | Inference service, quota, or billing is inactive | Check the online inference service in the TokenHub console |
| HTTP 403 | Account, model, IP allowlist, or resource permission issue | Check key permissions, region, and service status |
| HTTP 404 / model not found | Incorrect URL, path, model name, or service ID | Include `/v1` in the URL and query `/models` |
| HTTP 429 | Concurrency, rate, or quota limit | Honor `Retry-After`; otherwise use exponential backoff with jitter |
| HTTP 5xx | Temporary service failure | Retry only selected statuses a limited number of times |
| Connection refused | Self-hosted service is stopped or the port is wrong | Check the service process, bind address, firewall, and proxy |
| Chat-template-related 400 | Missing template or incompatible service version | Use the Hy3 tokenizer/chat template and update the framework |
| Empty `tool_calls` | Tool parser is disabled or the Schema is underspecified | Check the parser, tool_choice, and JSON Schema |
| Missing `reasoning_content` | Reasoning parser is disabled or the mode does not return it | Check server startup options and reasoning mode |
| Truncated output | `finish_reason=length` | Increase max_tokens or shorten the input |
| Empty streaming content | Only the first chunk is read or empty choices are mishandled | Iterate the complete stream and process usage separately |
| CUDA out of memory | Context, output budget, or concurrency is too high | Shorten context, reduce concurrency, or adjust parallelism |
| Client timeout | Model loading, long context, or deep reasoning takes longer | Adjust timeout or task size, or use streaming |

## 10. Production and Security Guidance

- Read API keys only from environment variables or a secret manager.
- Logs may contain redacted request IDs, status codes, latency, retry counts,
  and token usage.
- Do not log authorization headers, complete sensitive user content, or complete
  reasoning content.
- Select tools only from an explicit allowlist and validate arguments,
  permissions, timeouts, and output.
- Set explicit limits for tool loops, network retries, and total wait time.
- Do not assume fixed rate limits. Adjust concurrency from 429 responses,
  `Retry-After`, and application metrics.
- Warm up and run multiple trials for latency comparisons. Report median and
  P95 instead of drawing conclusions from one request.

## 11. Official References

- [TokenHub API instructions](https://cloud.tencent.com/document/product/1823/130078)
- [TokenHub language model overview](https://cloud.tencent.com/document/product/1823/130079)
- [TokenHub deep reasoning](https://cloud.tencent.com/document/product/1823/131208)
- [TokenHub interleaved reasoning](https://cloud.tencent.com/document/product/1823/130930)
- [Hy3 inference and deployment](README.md#deployment)
