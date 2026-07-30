# 05｜思考模式开关对比

完整程序：[05_reasoning_mode.py](05_reasoning_mode.py)

脚本对同一道题分别发送 `no_think` 和 `high`，记录总耗时、输出 Token 数、
`reasoning_content` 长度和最终回答。TokenHub 与自托管服务参数位置不同，
`common.reasoning_extra_body` 会根据 `HY3_API_MODE` 生成正确结构：

```python
# TokenHub 开启深度思考
{"thinking": {"type": "enabled"}, "reasoning_effort": "high"}

# TokenHub 关闭思考
{"thinking": {"type": "disabled"}}

# TokenHub 也支持 medium 推理深度
{"thinking": {"type": "enabled"}, "reasoning_effort": "medium"}

# 自托管 chat template
{"chat_template_kwargs": {"reasoning_effort": "high"}}
```

完整调用：

```python
response = client.chat.completions.create(
    model=settings.model,
    messages=[{"role": "user", "content": PROMPT}],
    temperature=0.9,
    top_p=1.0,
    max_tokens=1024 if effort == "no_think" else 16384,
    extra_body=reasoning_extra_body(settings.api_mode, effort),
)
```

## 输出示例

```text
=== reasoning_effort=no_think ===
elapsed: 1.532s
completion_tokens: 83
reasoning_chars: 0
answer: 净注水速度为 1/6 - 1/9 = 1/18……

=== reasoning_effort=high ===
elapsed: 3.876s
completion_tokens: 216
reasoning_chars: 294
answer: ……因此需要 18 小时。
```

不要凭一次调用断言某模式更快或更好。对真实业务题集多次运行，评估正确率、总耗时
和费用。思考模式需要更大的 `max_tokens`；不要把完整推理内容写入包含敏感数据的
日志。服务版本不支持某个取值时会返回 400，应以目标服务文档为准。

运行：`python 05_reasoning_mode.py`。
