# Hy3 API 快速开始

> 目标：5 分钟完成第一次调用，30 分钟掌握对话、流式输出、工具调用、思考模式和可靠重试。English: [quickstart.md](quickstart.md)。

Hy3 提供 OpenAI 兼容的 Chat Completions 接口。本指南覆盖 TokenHub 托管 API 和本地 vLLM/SGLang 服务。

## 1. 基础信息

| 项目 | TokenHub 广州 | TokenHub 新加坡 | 自托管 |
| --- | --- | --- | --- |
| Base URL | `https://tokenhub.tencentmaas.com/v1` | `https://tokenhub-intl.tencentmaas.com/v1` | 默认 `http://127.0.0.1:8000/v1` |
| API Key | TokenHub 控制台创建 | TokenHub 控制台创建 | 示例使用 `EMPTY` |
| Model | `hy3` | `hy3` | 由 `--served-model-name hy3` 设置 |
| 协议 | OpenAI Chat Completions | OpenAI Chat Completions | OpenAI 兼容接口 |

TokenHub 不支持跨地域调用，请使用资源开通地域对应的地址。先验证 Key 和模型状态：

```bash
curl https://tokenhub.tencentmaas.com/v1/models \
  -H "Authorization: Bearer $HY3_API_KEY"
```

PowerShell 建议使用 `curl.exe`，避免 `curl` 别名差异：

```powershell
curl.exe https://tokenhub.tencentmaas.com/v1/models `
  -H "Authorization: Bearer $env:HY3_API_KEY"
```

### API Key 安全

不要把 Key 写进源码、Notebook 输出、截图或 Git 历史。示例从 `HY3_API_KEY` 环境变量读取，`.env` 已被 Git 忽略。Key 泄露后应立即撤销并重新创建。

### 速率限制

仓库没有适用于所有用户的固定 RPM/TPM。TokenHub 限制取决于账号、地域和购买资源，以控制台及服务端响应为准；HTTP 429 应优先遵循 `Retry-After`。自托管吞吐取决于 GPU、并行配置、上下文长度和网关策略。业务代码不应假设固定限额。

## 2. 五分钟完成第一次调用

设置 Key：

```bash
export HY3_API_KEY="replace-with-your-key"       # Linux / macOS
```

```powershell
$env:HY3_API_KEY = "replace-with-your-key"       # Windows PowerShell
```

### curl

```bash
curl https://tokenhub.tencentmaas.com/v1/chat/completions \
  -H "Authorization: Bearer $HY3_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hy3",
    "messages": [{"role": "user", "content": "用一句话介绍 Hy3。"}],
    "temperature": 0.9,
    "top_p": 1.0,
    "max_tokens": 128,
    "stream": false
  }'
```

核心响应结构（实际 ID、内容和 Token 数会变化）：

```json
{
  "id": "chatcmpl-REDACTED",
  "object": "chat.completion",
  "model": "hy3",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "Hy3 是……"},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 16, "completion_tokens": 25, "total_tokens": 41}
}
```

### Python OpenAI SDK

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
    messages=[{"role": "user", "content": "用一句话介绍 Hy3。"}],
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

自托管只需改客户端：

```python
client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="EMPTY")
```

## 3. 参数说明

| 参数 | 类型 | 示例 | 说明 |
| --- | --- | --- | --- |
| `model` | string | `hy3` | 与 `/v1/models` 或 served model name 一致 |
| `messages` | array | system/user/assistant/tool | 多轮请求由客户端显式回传历史 |
| `temperature` | number | `0.9` | 控制随机性；与 `top_p` 通常不要同时大幅调整 |
| `top_p` | number | `1.0` | 核采样阈值 |
| `max_tokens` | integer | 按任务设置 | 输出上限；思考模式需预留更多预算 |
| `stop` | string/array | 自定义或不传 | 命中停止串时提前结束 |
| `stream` | boolean | `true`/`false` | 是否返回增量 chunk |
| `tools` | array | JSON Schema | 模型生成调用意图，业务方执行工具 |
| `tool_choice` | string | `auto` | TokenHub 工具场景使用自动选择 |

`finish_reason="length"` 表示输出达到限制，不应当作完整答案；可增大 `max_tokens` 或缩短输入。

## 4. 思考模式

TokenHub 用 `thinking.type` 开关思考，并在开启后用顶层 `reasoning_effort` 控制深度。Python SDK 通过 `extra_body` 传入：

```python
response = client.chat.completions.create(
    model="hy3",
    messages=[{"role": "user", "content": "证明根号 2 是无理数。"}],
    max_tokens=16384,
    extra_body={
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
    },
)
```

本地 vLLM/SGLang 使用仓库 chat template 约定：

```python
extra_body={"chat_template_kwargs": {"reasoning_effort": "high"}}
```

TokenHub 关闭思考使用 `{"thinking": {"type": "disabled"}}`；开启后可使用 `low`、`medium`、`high`。仓库自托管约定使用 `no_think`、`low`、`high`。`reasoning_content` 是提供商扩展字段，可兼容读取：

```python
reasoning = getattr(response.choices[0].message, "reasoning_content", "")
```

慢思考结合工具调用时，下一轮必须保留完整 assistant 消息，包括 `reasoning_content` 和 `tool_calls`。

## 5. 工具调用流程与安全

1. 发送工具 JSON Schema。
2. 检查 `tool_calls`。
3. 使用白名单查找工具并验证 JSON 参数。
4. 在业务侧执行工具。
5. 使用相同 `tool_call_id` 添加 `role="tool"` 消息。
6. 回传完整历史，直到最终回答。

生产代码必须设置最大工具轮数、超时和参数验证；绝不能执行模型返回的任意代码或命令。完整实现见 [`04_tool_calling.py`](examples/api/04_tool_calling.py)。

## 6. 常见错误排查

| 现象 | 常见原因 | 处理方式 |
| --- | --- | --- |
| HTTP 400 | 类型、消息顺序、工具 Schema 或能力不匹配 | 检查脱敏请求并逐项缩减；不要重试 |
| HTTP 401 | Key 缺失或无效 | 用 `/v1/models` 验证 Key 和 Bearer 头 |
| HTTP 403 | 账号或资源无权限 | 检查地域、开通状态和授权；不要重试 |
| HTTP 404 | URL、路径或模型名错误 | URL 应含 `/v1`，查询 `/v1/models` |
| HTTP 429 | 并发、速率或配额限制 | 遵循 `Retry-After`，否则退避加 jitter |
| HTTP 5xx | 暂时服务异常 | 只对选定状态做有限重试 |
| 连接失败 | 地址、代理、防火墙或本地服务问题 | 检查 DNS、TLS、端口和服务日志 |
| 超时 | 长上下文或深度思考 | 有意识地调 timeout 或缩短任务 |
| 输出截断 | `finish_reason=length` | 增大输出预算或压缩输入 |
| 流为空 | 只看首个 chunk 或没处理空 choices | 遍历全部 chunk，分开处理 usage |
| 工具循环卡住 | 历史不完整或没有轮数上限 | 原样回填并限制轮数 |

日志可记录 request ID、状态码、耗时、重试次数和 Token 用量，但不得记录 Key，也应谨慎记录用户内容和完整推理内容。

## 7. 示例和验证

[`examples/api`](examples/api/README.md) 提供六组完整 Python 示例：基础对话、流式解析、时延对比、工具循环、思考对比和可靠重试，并为每组示例提供独立说明。

官方参考：[TokenHub API](https://cloud.tencent.com/document/product/1823/130078)、[混元调用指南](https://cloud.tencent.com/document/product/1823/132252)、[交错式思考](https://cloud.tencent.com/document/product/1823/130930)。
