"""Shared configuration and response helpers for the Hy3 API examples."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

TOKENHUB_BASE_URL = "https://tokenhub.tencentmaas.com/v1"
LOCAL_BASE_URL = "http://127.0.0.1:8000/v1"


def configure_utf8_output() -> None:
    """Use UTF-8 for model output in Windows terminals."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    api_mode: str
    base_url: str
    api_key: str
    model: str
    timeout: float
    max_retries: int


def load_settings() -> Settings:
    """Load and validate settings without ever printing the API key."""

    load_dotenv()
    api_mode = os.getenv("HY3_API_MODE", "tokenhub").strip().lower()
    if api_mode not in {"tokenhub", "self_hosted"}:
        raise ValueError("HY3_API_MODE must be 'tokenhub' or 'self_hosted'")

    default_url = TOKENHUB_BASE_URL if api_mode == "tokenhub" else LOCAL_BASE_URL
    default_key = "" if api_mode == "tokenhub" else "EMPTY"
    api_key = os.getenv("HY3_API_KEY", default_key).strip()
    if not api_key:
        raise ValueError(
            "HY3_API_KEY is required for TokenHub. Copy .env.example to .env "
            "and fill in your key."
        )

    timeout = float(os.getenv("HY3_TIMEOUT", "60"))
    max_retries = int(os.getenv("HY3_MAX_RETRIES", "2"))
    if timeout <= 0:
        raise ValueError("HY3_TIMEOUT must be greater than 0")
    if max_retries < 0:
        raise ValueError("HY3_MAX_RETRIES must be 0 or greater")

    return Settings(
        api_mode=api_mode,
        base_url=os.getenv("HY3_BASE_URL", default_url).rstrip("/"),
        api_key=api_key,
        model=os.getenv("HY3_MODEL", "hy3").strip() or "hy3",
        timeout=timeout,
        max_retries=max_retries,
    )


def make_client(settings: Settings) -> OpenAI:
    """Create an OpenAI-compatible client with bounded SDK retries."""

    return OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
    )


def reasoning_extra_body(api_mode: str, effort: str) -> dict[str, Any]:
    """Build the provider-specific body for Hy3 reasoning mode.

    TokenHub uses ``thinking.type`` to enable/disable reasoning and a top-level
    ``reasoning_effort`` to select the depth after reasoning is enabled.
    Self-hosted vLLM/SGLang follows the repository chat-template convention.
    """

    if api_mode == "tokenhub":
        allowed = {"no_think", "low", "medium", "high"}
        if effort not in allowed:
            raise ValueError(f"TokenHub effort must be one of {sorted(allowed)}")
        if effort == "no_think":
            return {"thinking": {"type": "disabled"}}
        return {
            "thinking": {"type": "enabled"},
            "reasoning_effort": effort,
        }
    if api_mode == "self_hosted":
        allowed = {"no_think", "low", "high"}
        if effort not in allowed:
            raise ValueError(f"Self-hosted effort must be one of {sorted(allowed)}")
        return {"chat_template_kwargs": {"reasoning_effort": effort}}
    raise ValueError("api_mode must be 'tokenhub' or 'self_hosted'")


def extra_field(value: Any, field: str, default: Any = None) -> Any:
    """Read SDK-known or provider-specific fields from an OpenAI model."""

    direct = getattr(value, field, None)
    if direct is not None:
        return direct
    extra = getattr(value, "model_extra", None) or {}
    return extra.get(field, default)


def assistant_message_dict(message: Any) -> dict[str, Any]:
    """Serialize an assistant message for the next tool-calling turn.

    Provider-specific ``reasoning_content`` is preserved because interleaved
    reasoning needs it in subsequent requests.
    """

    result: dict[str, Any] = {
        "role": "assistant",
        "content": message.content or "",
    }
    reasoning = extra_field(message, "reasoning_content")
    if reasoning:
        result["reasoning_content"] = reasoning
    if message.tool_calls:
        result["tool_calls"] = [
            tool_call.model_dump(exclude_none=True) for tool_call in message.tool_calls
        ]
    return result


def parse_json_arguments(raw: str) -> dict[str, Any]:
    """Parse tool arguments and require a JSON object, not a scalar or list."""

    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Tool arguments are not valid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("Tool arguments must decode to a JSON object")
    return value


def print_usage(usage: Any) -> None:
    """Print token usage when the server supplies it."""

    if usage is None:
        print("usage: server did not return token statistics")
        return
    print(
        "usage: "
        f"prompt={usage.prompt_tokens}, "
        f"completion={usage.completion_tokens}, "
        f"total={usage.total_tokens}"
    )
