<p align="left">
  <a href="./03_streaming_vs_non_streaming.md">English</a>&nbsp;|&nbsp;中文
</p>

# 03｜非流式与流式时延对比

完整程序：[03_streaming_vs_non_streaming.py](03_streaming_vs_non_streaming.py)

## 指标定义

- **非流式总耗时**：发送请求到完整 response 返回。
- **流式 TTFT**：发送请求到收到第一个非空可见 `delta.content`。这不是 TCP 首字节
  时间，也不是第一个只有 role/思考内容的 chunk。
- **流式总耗时**：发送请求到流迭代结束。

测量使用单调高精度时钟 `time.perf_counter()`：

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

## 正确解读

脚本的一次运行只是演示测量方法，不是性能基准。两次请求可能生成不同长度内容，
还会受到冷启动、排队、网络、缓存和服务负载影响。正式比较至少应预热，固定地域
和参数，交替执行多轮，并报告中位数及 P95。

```text
=== Latency comparison (one sample, not a benchmark) ===
non-streaming total: 2.841s
streaming TTFT: 0.612s
streaming total: 3.104s
non-streaming chars: 174
streaming chars: 181
Run multiple warm samples before drawing performance conclusions.
```

流式的价值通常是更早显示内容，而不保证总耗时更短。运行：
`python 03_streaming_vs_non_streaming.py`。
