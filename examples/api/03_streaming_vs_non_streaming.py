"""Measure full-response latency and streaming time to first visible token."""

from time import perf_counter

from common import configure_utf8_output, load_settings, make_client

PROMPT = "用不超过 200 字解释大语言模型的流式输出。"


def run_non_streaming(client, model: str) -> tuple[float, str]:
    started = perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.9,
        top_p=1.0,
        max_tokens=300,
    )
    elapsed = perf_counter() - started
    return elapsed, response.choices[0].message.content or ""


def run_streaming(client, model: str) -> tuple[float | None, float, str]:
    started = perf_counter()
    first_content_at: float | None = None
    parts: list[str] = []
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.9,
        top_p=1.0,
        max_tokens=300,
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            if first_content_at is None:
                first_content_at = perf_counter()
            parts.append(content)
    finished = perf_counter()
    ttft = None if first_content_at is None else first_content_at - started
    return ttft, finished - started, "".join(parts)


def main() -> None:
    configure_utf8_output()
    settings = load_settings()
    client = make_client(settings)

    non_stream_total, non_stream_text = run_non_streaming(client, settings.model)
    stream_ttft, stream_total, stream_text = run_streaming(client, settings.model)

    print("=== Latency comparison (one sample, not a benchmark) ===")
    print(f"non-streaming total: {non_stream_total:.3f}s")
    print(
        "streaming TTFT: "
        + (f"{stream_ttft:.3f}s" if stream_ttft is not None else "no content received")
    )
    print(f"streaming total: {stream_total:.3f}s")
    print(f"non-streaming chars: {len(non_stream_text)}")
    print(f"streaming chars: {len(stream_text)}")
    print("Run multiple warm samples before drawing performance conclusions.")


if __name__ == "__main__":
    main()
