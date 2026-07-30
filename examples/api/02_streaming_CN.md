<p align="left">
  <a href="./02_streaming.md">English</a>&nbsp;|&nbsp;中文
</p>

# 02｜流式请求与逐 chunk 解析

完整程序：[02_streaming.py](02_streaming.py)

## 请求与解析

流式请求设置 `stream=True`，返回的是可迭代事件流，不是一个完整 response。
每个 chunk 可能只携带 role、正文的一小段、思考增量、结束原因或 usage；不能假设
每个 chunk 都有 choice 或 content。

```python
stream = client.chat.completions.create(
    model=settings.model,
    messages=[{"role": "user", "content": "解释流式输出。"}],
    stream=True,
    stream_options={"include_usage": True},
)
parts = []
for chunk in stream:
    if not chunk.choices:  # 最后的 usage-only chunk 可能走这里
        continue
    delta = chunk.choices[0].delta
    if delta.content:
        parts.append(delta.content)
        print(delta.content, end="", flush=True)
full_text = "".join(parts)
```

程序同时独立累积 `reasoning_content`，但默认不打印完整推理内容。工具调用的
arguments 也可能跨多个 chunk 到达；生产实现必须按 tool-call index/id 累积，不能
对单个片段直接做 `json.loads`。

## 输出示例

```text
assistant: 流式输出让用户在完整答案生成前就能看到内容……

=== Aggregated result ===
content_chars: 168
reasoning_chars: 0
finish_reason: stop
total_tokens: 102
```

如果服务没有实现 `stream_options.include_usage`，脚本会明确提示 usage 缺失，正文
仍可正常解析。运行：`python 02_streaming.py`。
