"""Hy3 tool calling: inspect one call, then execute a bounded tool loop."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from common import (
    assistant_message_dict,
    configure_utf8_output,
    load_settings,
    make_client,
    parse_json_arguments,
    reasoning_extra_body,
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的示例天气。",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名称"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    }
]


def get_weather(city: str) -> dict[str, Any]:
    """A deterministic local demo tool; replace it with a real weather API."""

    return {"city": city, "weather": "晴", "temperature_c": 26}


TOOL_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "get_weather": get_weather,
}


def execute_tool(name: str, raw_arguments: str) -> str:
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Tool is not allowed: {name}")
    arguments = parse_json_arguments(raw_arguments)
    result = TOOL_REGISTRY[name](**arguments)
    return json.dumps(result, ensure_ascii=False)


def run_tool_loop(client, settings, *, max_rounds: int = 4) -> str:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "需要天气信息时调用工具，不要猜测。"},
        {"role": "user", "content": "深圳天气如何？适合穿什么？"},
    ]
    extra_body = reasoning_extra_body(settings.api_mode, "no_think")

    for round_number in range(1, max_rounds + 1):
        response = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.9,
            top_p=1.0,
            max_tokens=512,
            extra_body=extra_body,
        )
        message = response.choices[0].message
        print(
            f"round {round_number}: finish_reason={response.choices[0].finish_reason}"
        )

        # No tool call means the model has produced its final answer.
        if not message.tool_calls:
            return message.content or ""

        messages.append(assistant_message_dict(message))
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            print(f"tool_call: {name}({tool_call.function.arguments})")
            try:
                result = execute_tool(name, tool_call.function.arguments)
            except (TypeError, ValueError) as exc:
                result = json.dumps({"error": str(exc)}, ensure_ascii=False)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    raise RuntimeError(f"Tool loop exceeded the safe limit of {max_rounds} rounds")


def main() -> None:
    configure_utf8_output()
    settings = load_settings()
    client = make_client(settings)
    answer = run_tool_loop(client, settings)
    print(f"final answer: {answer}")


if __name__ == "__main__":
    main()
