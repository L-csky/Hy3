<p align="left">
  <a href="./06_error_handling_retry.md">English</a>&nbsp;|&nbsp;中文
</p>

# 06｜错误处理、重试与退避

完整程序：[06_error_handling_retry.py](06_error_handling_retry.py)

## 错误分类

| 类型 | 是否重试 | 原因 |
| --- | --- | --- |
| 超时、连接失败 | 是，有限次数 | 常为短暂网络问题 |
| 408、409、429 | 是 | 请求超时、冲突或限流可能恢复 |
| 500、502、503、504 | 是 | 短暂服务异常 |
| 400 | 否 | 请求内容错误，原样重试无效 |
| 401、403 | 否 | 凭据或权限问题，重试无效 |
| 其他未知异常 | 否 | 避免掩盖程序错误 |

本示例把 SDK 的 `max_retries` 设为 0，让所有重试都由可见代码负责，避免 SDK 和
业务代码形成重试乘法。

## 等待策略

若响应有 `Retry-After`，支持秒数和 HTTP 日期两种格式，并按服务端要求等待；否则使用：

```text
min(base × 2^attempt + random(0, 1) × base, cap)
```

jitter 防止多个客户端在同一时刻再次冲击服务。除了 `max_attempts=4`，程序还有
`max_total_wait=60` 总等待预算；如果 `Retry-After` 超出剩余预算，程序会停止并将
控制权交给调用方，而不是提前重试。

```python
response = call_with_retry(
    lambda: client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": "解释指数退避。"}],
    )
)
```

## 输出示例

```text
attempt 1 failed with RateLimitError; retrying in 2.00s
attempt 2 failed with APIConnectionError; retrying in 2.37s
assistant: 指数退避是在连续失败后逐步增加等待时间的重试策略。
```

生产环境还应记录脱敏 request ID、状态码、尝试次数和延迟，并结合幂等性判断是否
能重试有副作用的业务操作。运行：`python 06_error_handling_retry.py`。
