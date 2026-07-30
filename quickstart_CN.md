<p align="left">
  <a href="./quickstart.md">English</a>&nbsp;｜&nbsp;中文
</p>

# Hy3 API 快速开始

本指南帮助开发者在约 5 分钟内完成第一次 Hy3 API 调用，并在约 30 分钟内掌握
对话、流式输出、工具调用、思考模式和可靠重试。

Hy3 提供 OpenAI 兼容的 Chat Completions API，支持两种 API 接入方式：

- **TokenHub 托管 API**：无需部署模型，开通服务并创建 API Key 后即可调用。
- **自托管 API**：先按照仓库 [README_CN.md](README_CN.md#推理和部署) 使用
  vLLM 或 SGLang 部署 Hy3，再调用该服务提供的 OpenAI 兼容接口。

本文只说明两种服务的 API 调用方式，不包含模型下载、GPU 规划或服务部署步骤。

## 1. 基础信息

| 项目 | TokenHub 广州 | TokenHub 新加坡 | 自托管默认值 |
| --- | --- | --- | --- |
| Base URL | `https://tokenhub.tencentmaas.com/v1` | `https://tokenhub-intl.tencentmaas.com/v1` | `http://127.0.0.1:8000/v1` |
| Chat endpoint | `/chat/completions` | `/chat/completions` | `/chat/completions` |
| API Key | TokenHub 控制台创建 | TokenHub 控制台创建 | 通常使用 `EMPTY` |
| Model | `hy3` 或服务 ID | `hy3` 或服务 ID | 与 `--served-model-name` 一致 |
| 协议 | OpenAI Chat Completions | OpenAI Chat Completions | OpenAI 兼容接口 |

TokenHub 不支持跨地域调用。API Key、服务资源和 Base URL 必须属于同一地域。
自定义在线推理服务应使用控制台显示的服务 ID，例如 `ep-xxxxxxxx`。

Hy3 模型上下文长度最高为 256K Token；实际可用长度还取决于服务配置、输入输出
预算、并发和可用显存。仓库没有适用于所有用户的固定 RPM/TPM：

- TokenHub 限制取决于账号、地域、套餐和推理服务配置。
- 自托管吞吐取决于 GPU、并行配置、网关、队列和上下文长度。
- 收到 HTTP 429 时应遵循 `Retry-After`，否则使用带 jitter 的指数退避。

## 2. 配置环境

安装 OpenAI Python SDK：

```bash
python -m pip install "openai>=1.30,<3"
```

### Linux / macOS

TokenHub 新加坡示例：

```bash
export HY3_BASE_URL="https://tokenhub-intl.tencentmaas.com/v1"
export HY3_API_KEY="replace-with-your-key"
export HY3_MODEL="hy3"
```

自托管示例：

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

不要把真实 API Key 写进源码、Notebook、截图或 Git 历史。Key 泄露后应立即撤销
并重新创建。

### 连通性检查

Linux / macOS：

```bash
curl "${HY3_BASE_URL}/models" \
  -H "Authorization: Bearer ${HY3_API_KEY}"
```

Windows PowerShell：

```powershell
curl.exe "$env:HY3_BASE_URL/models" `
  -H "Authorization: Bearer $env:HY3_API_KEY"
```

返回列表中的模型或服务 ID 应与 `HY3_MODEL` 一致。部分自托管框架还提供
`/health`，但该路径不是 OpenAI 协议的一部分，不能假设所有服务均支持。

## 3. 五分钟完成第一次调用

### curl

Linux / macOS：

```bash
curl "${HY3_BASE_URL}/chat/completions" \
  -H "Authorization: Bearer ${HY3_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @- <<JSON
{
  "model": "${HY3_MODEL}",
  "messages": [
    {"role": "user", "content": "请用一句话说明你能提供哪些帮助。"}
  ],
  "temperature": 0.9,
  "top_p": 1.0,
  "max_tokens": 128,
  "stream": false
}
JSON
```

Windows PowerShell：

```powershell
$body = @{
  model = $env:HY3_MODEL
  messages = @(
    @{ role = "user"; content = "请用一句话说明你能提供哪些帮助。" }
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

核心响应结构如下。实际 ID、内容和 Token 数会变化：

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
        "content": "示例回答内容……"
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
        {"role": "user", "content": "请用一句话说明你能提供哪些帮助。"},
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

多轮对话不会由服务端自动保存。客户端需要按顺序把之前的 `user` 和 `assistant`
消息重新放入下一次请求。完整实现见
[`01_basic_chat.py`](examples/api/01_basic_chat.py)。

## 4. 请求参数参考

| 参数 | 类型 | 示例 | 说明 |
| --- | --- | --- | --- |
| `model` | string | `hy3` | 使用 `/models` 返回的模型或服务 ID |
| `messages` | array | `system/user/assistant/tool` | 客户端显式维护的对话历史 |
| `temperature` | number | `0.9` | 控制采样随机性；仓库推荐值为 `0.9` |
| `top_p` | number | `1.0` | 核采样阈值；通常不要与 temperature 同时激进调整 |
| `max_tokens` | integer | `512` | 输出上限；思考模式应预留更大预算 |
| `stop` | string/array | `["Observation:"]` | 命中停止序列时结束生成 |
| `stream` | boolean | `true` | 返回增量 chunk，而不是等待完整回答 |
| `stream_options` | object | `{"include_usage": true}` | 请求在最后一个流式 chunk 中返回 usage |
| `tools` | array | JSON Schema | 定义模型可以选择的函数 |
| `tool_choice` | string/object | `auto` | 控制是否或如何选择工具 |
| `parallel_tool_calls` | boolean | `false` | 是否允许模型一次请求多个工具 |
| `response_format` | object | `{"type": "json_object"}` | 目标服务支持时约束输出格式 |

不同服务版本支持的参数可能不同。使用前应以目标服务文档和实际 `/models` 结果为准。

常见 `finish_reason`：

- `stop`：正常结束。
- `length`：达到输出预算，回答可能不完整。
- `tool_calls`：模型请求应用执行工具。

## 5. 思考模式

TokenHub 和自托管服务的参数位置不同：

| 场景 | 关闭思考 | 开启思考 |
| --- | --- | --- |
| TokenHub | `{"thinking":{"type":"disabled"}}` | `thinking.type=enabled`，深度为 `low/medium/high` |
| 自托管 | `reasoning_effort=no_think` | `reasoning_effort=low/high` |

### TokenHub

```python
response = client.chat.completions.create(
    model=os.getenv("HY3_MODEL", "hy3"),
    messages=[{"role": "user", "content": "证明根号 2 是无理数。"}],
    max_tokens=16384,
    extra_body={
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
    },
)
```

关闭思考：

```python
extra_body = {"thinking": {"type": "disabled"}}
```

### 自托管 vLLM/SGLang

```python
extra_body = {
    "chat_template_kwargs": {
        "reasoning_effort": "high",
    }
}
```

自托管约定使用 `no_think`、`low` 或 `high`。服务端还需启用对应的 reasoning
parser。提供商扩展字段 `reasoning_content` 可以兼容读取：

```python
reasoning = getattr(response.choices[0].message, "reasoning_content", "")
```

思考模式与工具调用结合时，下一轮必须保留完整 assistant 消息，包括
`reasoning_content` 和 `tool_calls`。不要把包含敏感业务数据的完整推理内容写入
日志。完整对比见 [`05_reasoning_mode.py`](examples/api/05_reasoning_mode.py)。

## 6. 流式响应

设置 `stream=True` 后，SDK 返回可迭代事件流。chunk 可能只包含 role、部分正文、
思考增量、结束原因或 usage，不能假设每个 chunk 都有正文：

```python
stream = client.chat.completions.create(
    model=os.getenv("HY3_MODEL", "hy3"),
    messages=[{"role": "user", "content": "解释流式输出。"}],
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

工具参数也可能跨多个流式 chunk 到达，生产代码必须按 tool-call index 或 ID
累积后再解析。完整实现见 [`02_streaming.py`](examples/api/02_streaming.py)。

## 7. 工具调用

自托管服务需要先启用工具解析：

- vLLM：使用 `--tool-call-parser hy_v3` 和 `--enable-auto-tool-choice`。
- SGLang：使用仓库 README 中的 Hunyuan 工具解析器配置。

应用侧完整流程：

1. 定义 `tools` JSON Schema。
2. 使用 `tool_choice="auto"` 发送请求。
3. 检查 assistant 返回的 `tool_calls`。
4. 通过白名单确认工具名，并验证 JSON 参数。
5. 在业务侧执行工具。
6. 使用相同 `tool_call_id` 添加 `role="tool"` 的结果消息。
7. 回传完整历史，直到模型输出最终回答。

生产代码必须设置最大工具轮数、工具超时、权限校验和输出长度限制。绝不能使用
`eval`、`exec` 或 Shell 直接执行模型生成的内容。完整实现见
[`04_tool_calling.py`](examples/api/04_tool_calling.py)。

## 8. 示例索引

| 说明文档 | 示例脚本 | 演示内容 |
| --- | --- | --- |
| [基础对话](examples/api/01_basic_chat_CN.md) | [`01_basic_chat.py`](examples/api/01_basic_chat.py) | 单轮、多轮及 usage |
| [流式输出](examples/api/02_streaming_CN.md) | [`02_streaming.py`](examples/api/02_streaming.py) | 逐 chunk 解析与聚合 |
| [时延对比](examples/api/03_streaming_vs_non_streaming_CN.md) | [`03_streaming_vs_non_streaming.py`](examples/api/03_streaming_vs_non_streaming.py) | TTFT 与总耗时 |
| [工具调用](examples/api/04_tool_calling_CN.md) | [`04_tool_calling.py`](examples/api/04_tool_calling.py) | 一次调用及有界工具循环 |
| [思考模式](examples/api/05_reasoning_mode_CN.md) | [`05_reasoning_mode.py`](examples/api/05_reasoning_mode.py) | `no_think` 与 `high` 对比 |
| [错误重试](examples/api/06_error_handling_retry_CN.md) | [`06_error_handling_retry.py`](examples/api/06_error_handling_retry.py) | 错误分类与指数退避 |

每个说明文档均包含请求流程、响应解析、注意事项和脱敏输出示例。安装及运行方式见
[`examples/api/README_CN.md`](examples/api/README_CN.md)。

## 9. 常见错误排查

| 现象 | 常见原因 | 处理方式 |
| --- | --- | --- |
| HTTP 400 | 参数类型、消息顺序、工具 Schema 或能力不匹配 | 检查脱敏请求并逐项缩减；不要原样重试 |
| HTTP 401 / `401002` | Key 缺失、无效或地域不匹配 | 核对 Key 和 Base URL 地域，用 `/models` 验证 |
| HTTP 402 / endpoint inactive | 推理服务未激活、额度或计费未启用 | 在 TokenHub 控制台检查在线推理服务 |
| HTTP 403 | 账号、模型、IP 白名单或资源无权限 | 检查 Key 权限、地域和服务状态 |
| HTTP 404 / model not found | URL、路径、模型名或服务 ID 错误 | URL 应包含 `/v1`，并查询 `/models` |
| HTTP 429 | 并发、速率或配额限制 | 遵循 `Retry-After`，否则指数退避加 jitter |
| HTTP 5xx | 暂时服务异常 | 仅对选定状态进行有限次数重试 |
| Connection refused | 自托管服务未启动或端口错误 | 检查服务进程、监听地址、防火墙和代理 |
| chat template 相关 400 | 模板缺失或与服务版本不兼容 | 使用 Hy3 tokenizer/chat template 并更新框架 |
| `tool_calls` 为空 | 未启用工具解析器或 Schema 描述不足 | 检查 parser、tool_choice 和 JSON Schema |
| 缺少 `reasoning_content` | 未启用 reasoning parser 或当前模式不返回 | 检查服务启动参数和思考模式 |
| 输出截断 | `finish_reason=length` | 增大 max_tokens 或压缩输入 |
| 流式正文为空 | 只读取首个 chunk 或忽略空 choices | 遍历完整事件流并分别处理 usage |
| CUDA OOM | 上下文、输出预算或并发过高 | 缩短上下文、降低并发或调整并行配置 |
| 客户端超时 | 模型加载、长上下文或深度思考耗时较长 | 调整 timeout、任务规模或使用流式输出 |

## 10. 生产与安全建议

- API Key 只从环境变量或密钥管理服务读取。
- 日志可记录脱敏 request ID、状态码、耗时、重试次数和 Token 用量。
- 不记录 Authorization Header、完整用户敏感内容或完整推理内容。
- 工具只能从显式白名单中选择，并对参数、权限、超时和输出做校验。
- 为工具循环、网络重试和总等待时间设置明确上限。
- 不要假设固定限流；根据 429、`Retry-After` 和业务指标动态调节并发。
- 时延比较应预热并运行多轮，报告中位数和 P95，不能用单次结果下结论。

## 11. 官方参考

- [TokenHub API 使用说明](https://cloud.tencent.com/document/product/1823/130078)
- [TokenHub 语言模型调用概览](https://cloud.tencent.com/document/product/1823/130079)
- [TokenHub 深度思考](https://cloud.tencent.com/document/product/1823/131208)
- [TokenHub 交错式思考](https://cloud.tencent.com/document/product/1823/130930)
- [Hy3 推理和部署](README_CN.md#推理和部署)
