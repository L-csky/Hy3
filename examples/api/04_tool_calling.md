<p align="left">
  English&nbsp;|&nbsp;<a href="./04_tool_calling_CN.md">Chinese</a>
</p>

# 04 | One Tool Call and a Multi-Round Tool Loop

Complete program: [04_tool_calling.py](04_tool_calling.py)

## Complete Protocol Loop

1. Send a request with a `tools` JSON Schema and `tool_choice="auto"`.
2. Read the assistant's `tool_calls` instead of guessing tools from prose.
3. Resolve the tool through an allowlist and verify that decoded JSON arguments
   form an object.
4. Execute the function in the application and serialize its result as text.
5. Append the complete assistant message and a `role="tool"` result to
   `messages`.
6. Continue until the assistant stops requesting tools or the safety limit is
   reached.

First request:

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

Return the tool result:

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

`assistant_message_dict` preserves `content`, `tool_calls`, and the
`reasoning_content` required by reasoning-plus-tool flows. The example weather
function returns fixed data and does not access the internet.

## Security Boundaries

- Allow only functions registered in `TOOL_REGISTRY`.
- Do not use `eval` or `exec`, and do not execute model-generated commands.
- Return controlled tool errors for invalid JSON or mismatched arguments.
- Limit the tool loop to four rounds.
- Real tools also require permission checks, timeouts, auditing, and output
  limits.

```text
round 1: finish_reason=tool_calls
tool_call: get_weather({"city":"Shenzhen"})
round 2: finish_reason=stop
final answer: The example weather in Shenzhen is sunny, 26 C...
```

Tool selection varies with sampling; the output is structural only. Run with
`python 04_tool_calling.py`.
