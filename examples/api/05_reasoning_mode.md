<p align="left">
  English&nbsp;|&nbsp;<a href="./05_reasoning_mode_CN.md">Chinese</a>
</p>

# 05 | Comparing Reasoning Modes

Complete program: [05_reasoning_mode.py](05_reasoning_mode.py)

The script sends the same problem with `no_think` and `high`, recording total
latency, output tokens, `reasoning_content` length, and the final answer.
TokenHub and self-hosted services place these parameters differently.
`common.reasoning_extra_body` generates the correct structure from
`HY3_API_MODE`:

```python
# Enable deep reasoning on TokenHub.
{"thinking": {"type": "enabled"}, "reasoning_effort": "high"}

# Disable reasoning on TokenHub.
{"thinking": {"type": "disabled"}}

# TokenHub also supports medium reasoning depth.
{"thinking": {"type": "enabled"}, "reasoning_effort": "medium"}

# Self-hosted chat template.
{"chat_template_kwargs": {"reasoning_effort": "high"}}
```

Complete call:

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

## Example Output

```text
=== reasoning_effort=no_think ===
elapsed: 1.532s
completion_tokens: 83
reasoning_chars: 0
answer: The net fill rate is 1/6 - 1/9 = 1/18...

=== reasoning_effort=high ===
elapsed: 3.876s
completion_tokens: 216
reasoning_chars: 294
answer: Therefore, filling the pool takes 18 hours.
```

Do not conclude that one mode is faster or better from a single request.
Evaluate accuracy, total latency, and cost over repeated runs on a real task
set. Reasoning needs a larger `max_tokens` budget. Do not log complete reasoning
that contains sensitive data. An unsupported value returns HTTP 400, so follow
the target service documentation.

Run with `python 05_reasoning_mode.py`.
