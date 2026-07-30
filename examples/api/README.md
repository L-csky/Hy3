<p align="left">
  English&nbsp;|&nbsp;<a href="./README_CN.md">Chinese</a>
</p>

# Runnable Hy3 API Examples

This directory accompanies the repository's
[English quickstart](../../quickstart.md). The six examples are independent and
can be run in numbered order.

## 1. Set Up the Environment

```bash
cd examples/api
python -m venv .venv
```

Activate the virtual environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the dependencies and create a local configuration:

```bash
python -m pip install -r requirements.txt
cp .env.example .env                 # Linux / macOS
Copy-Item .env.example .env          # Windows PowerShell
```

Edit `.env` and add your TokenHub API key. For a local vLLM/SGLang service, set
`HY3_API_MODE=self_hosted` and use the local service URL.

## 2. Example Index

| No. | Script | Learning goal | Detailed guide |
| --- | --- | --- | --- |
| 01 | `01_basic_chat.py` | Single-turn and multi-turn chat, plus usage | [Guide](01_basic_chat.md) |
| 02 | `02_streaming.py` | Per-chunk parsing and safe aggregation | [Guide](02_streaming.md) |
| 03 | `03_streaming_vs_non_streaming.py` | Time to first token and total latency | [Guide](03_streaming_vs_non_streaming.md) |
| 04 | `04_tool_calling.py` | One call and a bounded tool loop | [Guide](04_tool_calling.md) |
| 05 | `05_reasoning_mode.py` | Reasoning on/off comparison | [Guide](05_reasoning_mode.md) |
| 06 | `06_error_handling_retry.py` | Error classification and backoff | [Guide](06_error_handling_retry.md) |

Run the examples:

```bash
python 01_basic_chat.py
python 02_streaming.py
python 03_streaming_vs_non_streaming.py
python 04_tool_calling.py
python 05_reasoning_mode.py
python 06_error_handling_retry.py
```

## 3. Security and Reproducibility

- API keys are read only from environment variables or a Git-ignored `.env`.
- The examples never print an API key.
- Documented outputs are redacted structural examples. Actual content and
  latency vary between runs.
- The tool-calling example executes only local functions explicitly registered
  in the code. It does not execute arbitrary model-generated code.
- The retry example limits both attempts and total wait time to prevent
  unbounded retries.
