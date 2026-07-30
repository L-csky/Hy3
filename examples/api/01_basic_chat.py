"""Hy3 basic chat: one turn, multiple turns, and response parsing."""

from common import configure_utf8_output, load_settings, make_client, print_usage


def main() -> None:
    configure_utf8_output()
    settings = load_settings()
    client = make_client(settings)

    print("=== Single-turn chat ===")
    response = client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": "用三句话介绍 Hy3。"}],
        temperature=0.9,
        top_p=1.0,
        max_tokens=256,
    )
    choice = response.choices[0]
    print(f"id: {response.id}")
    print(f"finish_reason: {choice.finish_reason}")
    print(f"assistant: {choice.message.content}")
    print_usage(response.usage)

    print("\n=== Multi-turn chat ===")
    messages = [
        {"role": "system", "content": "你是一位简洁的 Python 助教。"},
        {"role": "user", "content": "列表推导式是什么？请给一个例子。"},
    ]
    first = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=0.9,
        top_p=1.0,
        max_tokens=256,
    )
    first_text = first.choices[0].message.content or ""
    print(f"assistant[1]: {first_text}")

    # The API is stateless: append both sides of the previous turn explicitly.
    messages.extend(
        [
            {"role": "assistant", "content": first_text},
            {"role": "user", "content": "把例子改成只保留偶数。"},
        ]
    )
    second = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=0.9,
        top_p=1.0,
        max_tokens=256,
    )
    print(f"assistant[2]: {second.choices[0].message.content}")
    print_usage(second.usage)


if __name__ == "__main__":
    main()
