# Hy3 API 可运行示例

本目录对应仓库根目录的 [中文快速开始](../../quickstart_CN.md) 和
[English quickstart](../../quickstart.md)。六个示例互相独立，可按编号依次运行。

## 1. 准备环境

```bash
cd examples/api
python -m venv .venv
```

激活虚拟环境：

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

安装依赖并创建本地配置：

```bash
python -m pip install -r requirements.txt
cp .env.example .env                 # Linux / macOS
Copy-Item .env.example .env          # Windows PowerShell
```

编辑 `.env`，填入 TokenHub API Key。若使用本地 vLLM/SGLang，则切换
`HY3_API_MODE=self_hosted`，并使用本地服务地址。

## 2. 示例索引

| 编号 | 脚本 | 学习目标 | 配套文档 |
| --- | --- | --- | --- |
| 01 | `01_basic_chat.py` | 单轮、多轮、usage | [说明](01_basic_chat.md) |
| 02 | `02_streaming.py` | 逐 chunk 解析与安全拼接 | [说明](02_streaming.md) |
| 03 | `03_streaming_vs_non_streaming.py` | TTFT 与总耗时 | [说明](03_streaming_vs_non_streaming.md) |
| 04 | `04_tool_calling.py` | 单次调用与有界工具循环 | [说明](04_tool_calling.md) |
| 05 | `05_reasoning_mode.py` | 思考模式开/关对比 | [说明](05_reasoning_mode.md) |
| 06 | `06_error_handling_retry.py` | 分类重试与退避 | [说明](06_error_handling_retry.md) |

运行方式：

```bash
python 01_basic_chat.py
python 02_streaming.py
python 03_streaming_vs_non_streaming.py
python 04_tool_calling.py
python 05_reasoning_mode.py
python 06_error_handling_retry.py
```

## 3. 安全与复现约定

- API Key 只从环境变量或被 Git 忽略的 `.env` 读取。
- 示例不会打印 API Key。
- 文档中的输出是脱敏的格式示例；延迟和内容以实际运行结果为准。
- 工具调用示例只执行代码中显式注册的本地函数，不执行模型生成的任意代码。
- 重试示例设置最大尝试次数和最大等待时间，避免无限重试。
