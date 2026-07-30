<p align="left">
  English&nbsp;|&nbsp;<a href="./01_basic_chat_CN.md">Chinese</a>
</p>

# 01 | Basic Chat: Single-Turn and Multi-Turn

Complete program: [01_basic_chat.py](01_basic_chat.py)

## Request Flow

A single-turn request contains one user message. The script sends `model`,
`messages`, sampling parameters, and `max_tokens`, then reads `response.id`, the
first choice, `finish_reason`, the assistant content, and usage.

The server does not automatically preserve a multi-turn conversation. The
second request must contain, in order, the system instruction, first user
message, first assistant response, and second user message. Omitting the
assistant history removes context from the previous turn. Applications should
also control context growth as the conversation becomes longer.

Core request and response parsing:

```python
response = client.chat.completions.create(
    model=settings.model,
    messages=[{"role": "user", "content": "Introduce Hy3 in three sentences."}],
    temperature=0.9,
    top_p=1.0,
    max_tokens=256,
)
choice = response.choices[0]
print(choice.message.content)
print(choice.finish_reason)
print(response.usage.total_tokens if response.usage else "no usage")
```

## Response Fields

- `choices[0].message.content`: Final text.
- `finish_reason=stop`: Generation ended naturally or matched a stop condition.
- `finish_reason=length`: The output budget was reached and the answer may be
  incomplete.
- `usage`: Input, output, and total token counts. Compatible services may omit
  this field.

## Example Output

The following shows only the output structure. Content and token counts vary:

```text
=== Single-turn chat ===
id: chatcmpl-REDACTED
finish_reason: stop
assistant: Hy3 is...
usage: prompt=18, completion=72, total=90

=== Multi-turn chat ===
assistant[1]: A list comprehension...
assistant[2]: You can write [x for x in values if x % 2 == 0].
usage: prompt=96, completion=35, total=131
```

Run with `python 01_basic_chat.py`.
