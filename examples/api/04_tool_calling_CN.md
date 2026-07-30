<p align="left">
  <a href="./04_tool_calling.md">English</a>&nbsp;|&nbsp;中文
</p>

# 04｜一次工具调用与多轮工具循环

完整程序：[04_tool_calling.py](04_tool_calling.py)

## 完整协议循环

1. 请求包含 `tools` JSON Schema 和 `tool_choice="auto"`。
2. 解析 assistant 的 `tool_calls`，而不是从自然语言猜工具。
3. 用白名单解析工具名，使用 `json.loads` 后确认参数是对象。
4. 业务侧执行函数，将结果序列化为字符串。
5. 将完整 assistant 消息和 `role="tool"` 结果追加到 messages。
6. 继续请求，直到 assistant 不再调用工具或达到安全轮数。

第一轮请求：

```python
response = client.chat.completions.create(
    model=settings.model,
    messages=messages,
    tools=TOOLS,
    tool_choice="auto",
    max_tokens=512,
    extra_body=reasoning_extra_body(settings.api_mode, "no_think"),
)
```

回填工具结果：

```python
messages.append(assistant_message_dict(message))
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": execute_tool(name, tool_call.function.arguments),
    }
)
```

`assistant_message_dict` 会保留 `content`、`tool_calls` 以及慢思考工具流程需要的
`reasoning_content`。示例天气函数返回固定数据，不调用外网，便于复现。

## 安全边界

- 只允许 `TOOL_REGISTRY` 中的函数。
- 不使用 `eval`/`exec`，不执行模型生成的命令。
- 参数 JSON 错误或函数参数不匹配时，把受控错误作为工具结果返回。
- 工具循环最多四轮，防止模型反复调用。
- 真实工具还需要权限校验、超时、审计和输出长度限制。

```text
round 1: finish_reason=tool_calls
tool_call: get_weather({"city":"深圳"})
round 2: finish_reason=stop
final answer: 深圳当前示例天气为晴，26°C……
```

模型是否调用工具具有采样差异；输出仅为格式示例。运行：`python 04_tool_calling.py`。
