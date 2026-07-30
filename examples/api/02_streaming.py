"""Hy3 streaming chat with per-chunk parsing and final aggregation."""

from common import configure_utf8_output, extra_field, load_settings, make_client


def main() -> None:
    configure_utf8_output()
    settings = load_settings()
    client = make_client(settings)
    stream = client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": "解释为什么流式输出能改善用户体验。"}],
        temperature=0.9,
        top_p=1.0,
        max_tokens=600,
        stream=True,
        stream_options={"include_usage": True},
    )

    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    finish_reason = None
    usage = None

    print("assistant: ", end="", flush=True)
    for chunk in stream:
        if chunk.usage is not None:
            usage = chunk.usage
        if not chunk.choices:
            continue

        choice = chunk.choices[0]
        finish_reason = choice.finish_reason or finish_reason
        delta = choice.delta
        reasoning = extra_field(delta, "reasoning_content", "") or ""
        if reasoning:
            reasoning_parts.append(reasoning)
        if delta.content:
            content_parts.append(delta.content)
            print(delta.content, end="", flush=True)

        # Uncomment this line to inspect every raw protocol chunk.
        # print(f"\nchunk={chunk.model_dump_json()}")

    full_content = "".join(content_parts)
    full_reasoning = "".join(reasoning_parts)
    print("\n\n=== Aggregated result ===")
    print(f"content_chars: {len(full_content)}")
    print(f"reasoning_chars: {len(full_reasoning)}")
    print(f"finish_reason: {finish_reason}")
    if usage:
        print(f"total_tokens: {usage.total_tokens}")
    else:
        print("usage: server did not include usage in the final chunk")


if __name__ == "__main__":
    main()
