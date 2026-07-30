# 01｜基础对话：单轮与多轮

完整程序：[01_basic_chat.py](01_basic_chat.py)

## 请求流程

单轮请求只包含一条 user 消息。脚本发送 `model`、`messages`、采样参数和
`max_tokens`，然后解析 `response.id`、第一条 choice、`finish_reason`、assistant
正文和 usage。

多轮对话并不是服务端自动保存会话。第二次请求必须按顺序包含：system 指令、
第一条 user、第一条 assistant、第二条 user。遗漏 assistant 历史会让模型失去
上一轮回答；历史不断增长时，应在业务侧控制上下文长度。

核心请求和解析：

```python
response = client.chat.completions.create(
    model=settings.model,
    messages=[{"role": "user", "content": "用三句话介绍 Hy3。"}],
    temperature=0.9,
    top_p=1.0,
    max_tokens=256,
)
choice = response.choices[0]
print(choice.message.content)
print(choice.finish_reason)
print(response.usage.total_tokens if response.usage else "no usage")
```

## 响应字段

- `choices[0].message.content`：最终文本。
- `finish_reason=stop`：自然或 stop 条件结束。
- `finish_reason=length`：达到输出预算，答案可能不完整。
- `usage`：输入、输出和总 Token 数；兼容服务可以不返回该字段。

## 输出示例

以下只展示格式，内容与 Token 数以运行结果为准：

```text
=== Single-turn chat ===
id: chatcmpl-REDACTED
finish_reason: stop
assistant: Hy3 是……
usage: prompt=18, completion=72, total=90

=== Multi-turn chat ===
assistant[1]: 列表推导式……
assistant[2]: 可以写成 [x for x in values if x % 2 == 0]。
usage: prompt=96, completion=35, total=131
```

运行：`python 01_basic_chat.py`。
