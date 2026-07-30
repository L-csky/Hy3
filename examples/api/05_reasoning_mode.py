"""Compare Hy3 direct-answer and deep-reasoning modes."""

from time import perf_counter

from common import (
    configure_utf8_output,
    extra_field,
    load_settings,
    make_client,
    reasoning_extra_body,
)

PROMPT = (
    "一个水池有进水管和出水管。单开进水管 6 小时注满，"
    "单开出水管 9 小时排空。两管同时打开，多久注满？说明计算过程。"
)


def run_mode(client, settings, effort: str) -> dict[str, object]:
    started = perf_counter()
    response = client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.9,
        top_p=1.0,
        max_tokens=1024 if effort == "no_think" else 16384,
        extra_body=reasoning_extra_body(settings.api_mode, effort),
    )
    elapsed = perf_counter() - started
    message = response.choices[0].message
    usage = response.usage
    return {
        "effort": effort,
        "elapsed": elapsed,
        "reasoning": extra_field(message, "reasoning_content", "") or "",
        "content": message.content or "",
        "completion_tokens": None if usage is None else usage.completion_tokens,
    }


def main() -> None:
    configure_utf8_output()
    settings = load_settings()
    client = make_client(settings)
    for effort in ("no_think", "high"):
        result = run_mode(client, settings, effort)
        print(f"\n=== reasoning_effort={effort} ===")
        print(f"elapsed: {result['elapsed']:.3f}s")
        print(f"completion_tokens: {result['completion_tokens']}")
        print(f"reasoning_chars: {len(str(result['reasoning']))}")
        print(f"answer: {result['content']}")

    print("\nLatency and token counts vary; compare several runs for evaluation.")


if __name__ == "__main__":
    main()
