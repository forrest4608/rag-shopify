# Legacy Project Map — RAG Challenge 2

> 本文档基于对所有源码、配置、数据目录和历史记录的逐文件阅读生成。
> 未修改任何业务代码。

---

## Project Type
企业年报问答系统（RAG: Retrieval-Augmented Generation）。
原为 RAG Challenge 竞赛冠军方案，当前正在被改造为使用阿里通义千问（DashScope/Qwen）的国产化版本。

## Runtime / Framework / Language
- **Language**: Python 3.11（推荐；项目已通过 pyenv 安装 3.11.13）
- **Core Frameworks**: LangChain 0.3.3, FAISS, rank-bm25, Docling 2.14.0
- **LLM SDKs**: openai, google-generativeai, dashscope
- **CLI**: click 8.1.7
- **Data Validation**: pydantic 2.9.2

## Package Manager
- `pip` + `requirements.txt` + `setup.py`（editable install `pip install -e .`）
- 项目使用独立 venv: `./venv/`（Python 3.11.13 via pyenv）

## Startup Commands
```bash
# 激活虚拟环境
source ./venv/bin/activate

# 方式一：CLI（需在数据集目录运行）
cd data/test_set
python ../../main.py process-questions --config max_nst_o3m

# 方式二：直接运行 pipeline（从项目根目录）
python -m src.pipeline

# 方式三：CLI 帮助
python main.py --help
```

## Test Commands
```bash
# 运行已有单元测试
./venv/bin/python -m pytest tests/ -v

# 当前仅覆盖 text_splitter.py (15 tests)
```

## Build Commands
```bash
pip install -e . -r requirements.txt
```

## Main Entry Points

| 文件 | 作用 | 运行方式 |
|------|------|----------|
| `main.py` | CLI 入口（click） | `python main.py <command>` |
| `src/pipeline.py` | 全流程编排 + 直接执行 | `python -m src.pipeline` |
| `1-情感分析-Qwen.py` | 独立实验脚本（Qwen 情感分析） | `python 1-情感分析-Qwen.py` |
| `dashscope-embedding-1.py` | 独立实验脚本（DashScope Embedding） | `python dashscope-embedding-1.py` |

## Main Business Modules

| 模块 | 核心职责 | 关键类/函数 | 行数 |
|------|----------|-------------|------|
| `pipeline.py` | 全流程编排、配置管理 | `Pipeline`, `RunConfig`, `PipelineConfig` | 494 |
| `api_requests.py` | 多 LLM Provider 统一接口 | `APIProcessor`, `BaseOpenaiProcessor`, `BaseDashscopeProcessor`, `BaseGeminiProcessor`, `BaseIBMAPIProcessor` | 694 |
| `questions_processing.py` | 问答主逻辑、多公司路由 | `QuestionsProcessor` | 525 |
| `retrieval.py` | 向量/BM25/混合检索 | `VectorRetriever`, `BM25Retriever`, `HybridRetriever` | 333 |
| `reranking.py` | LLM 重排序 | `LLMReranker`, `JinaReranker` | 225 |
| `prompts.py` | 所有 Prompt + Pydantic Schema | 7个 Prompt 类 + 多个 `AnswerSchema` | 472 |
| `ingestion.py` | 向量库/BM25索引构建 | `VectorDBIngestor`, `BM25Ingestor` | 146 |
| `text_splitter.py` | 文本分块 | `TextSplitter` | 127 |
| `parsed_reports_merging.py` | 解析结果规整 | `PageTextPreparation` | 436 |
| `pdf_parsing.py` | PDF 解析（Docling） | `PDFParser` | ~700 |
| `tables_serialization.py` | 表格 LLM 序列化 | `TableSerializer` | ~480 |
| `api_request_parallel_processor.py` | 异步批量 API 调用 | `process_api_requests_from_file` | ~530 |

## Data Flow

```
PDF Reports (data/test_set/pdf_reports/*.pdf)
    │
    ▼ [pdf_parsing.py → Docling]
debug_data/01_parsed_reports/*.json     ← 结构化 JSON（含表格、元数据）
    │
    ▼ [tables_serialization.py → LLM]   (可选)
debug_data/01_parsed_reports/*.json     ← 表格增加 serialized 字段
    │
    ▼ [parsed_reports_merging.py]
debug_data/02_merged_reports/*.json     ← 每页规整为 Markdown 文本
    │
    ▼ [parsed_reports_merging.py]        (可选)
debug_data/03_reports_markdown/*.md     ← 纯文本，供人工审查
    │
    ▼ [text_splitter.py]
databases/chunked_reports/*.json        ← 按 Token 分块
    │
    ▼ [ingestion.py]
databases/vector_dbs/*.faiss            ← FAISS 向量索引
databases/bm25_dbs/*.pkl                ← BM25 索引
    │
    ▼ [retrieval.py + reranking.py]      ← 检索 + 重排
    │
    ▼ [questions_processing.py + api_requests.py + prompts.py]
answers*.json                           ← 最终答案文件
```

## External Dependencies

| 依赖 | 用途 | 配置 |
|------|------|------|
| **DashScope (Qwen)** | 问答生成 + Embedding + 重排 | `DASHSCOPE_API_KEY` |
| **OpenAI** | 问答生成 + Embedding（原版） | `OPENAI_API_KEY` |
| **Google Gemini** | 大上下文问答 | `GEMINI_API_KEY` |
| **Jina AI** | 重排序（可选） | `JINA_API_KEY` |
| **Hugging Face Hub** | Docling 模型下载 | 自动下载到 `~/.cache/huggingface` |

## Database / Storage
- **FAISS**: `data/test_set/databases/vector_dbs/*.faiss` — 向量索引文件
- **BM25**: `data/test_set/databases/bm25_dbs/*.pkl` — 关键词索引
- **Chunked Reports**: `data/test_set/databases/chunked_reports/*.json` — 分块文档
- **中间数据**: `data/test_set/debug_data/01~03_*` — 各阶段中间产物
- **预置数据集**: 提供 `databases.zip` 和 `debug_data.zip` 可跳过解析阶段

## Configuration Files
- `env` → 重命名为 `.env`，存放 API Keys
- `requirements.txt` — 依赖锁定（`faiss-cpu` 已放宽为 `>=1.8.0`）
- `setup.py` — 最小化 setuptools 配置，包名 `erc2`
- `src/pipeline.py` — 内含 12 套预定义运行配置（`RunConfig`），当前默认使用 `max_nst_o3m`（Qwen-Turbo）

## Areas With Tests
- `tests/test_text_splitter.py` — 15 个用例，覆盖 `TextSplitter` 的 4 个方法

## Areas Without Tests (High Risk)

| 模块 | 风险等级 | 原因 |
|------|---------|------|
| `api_requests.py` | 🔴 极高 | 694 行，4 个 Provider，网络调用 + JSON 解析 + 重试 |
| `questions_processing.py` | 🔴 极高 | 525 行，复杂路由 + 多公司比较 + 引用校验 |
| `retrieval.py` | 🟠 高 | 333 行，3 种检索器，涉及向量计算和文件 I/O |
| `reranking.py` | 🟠 高 | LLM 评分解析逻辑，DashScope 分支返回硬编码 0.0 分 |
| `prompts.py` | 🟡 中 | Prompt 变更直接影响答案质量，但无自动化回归检测 |
| `parsed_reports_merging.py` | 🟡 中 | 436 行复杂文本清洗逻辑 |
| `ingestion.py` | 🟡 中 | DashScope Embedding 调用有大量调试 print |

## High-Risk Files
- `src/api_requests.py` — 所有外部 API 交互的单点，`BaseDashscopeProcessor` 不支持结构化输出（仅返回 `{"final_answer": content}`）
- `src/reranking.py` — DashScope 分支的 `relevance_score` 硬编码为 `0.0`，导致重排功能实际无效
- `src/pipeline.py` — 入口逻辑耦合度高，手动注释/反注释切换步骤

## Hard-to-Change Areas
- **Docling 集成** (`pdf_parsing.py`): 深度耦合特定版本的 Docling 模型和数据格式
- **Prompt 体系** (`prompts.py`): 所有 Prompt 已翻译为中文，修改任何措辞可能显著影响 LLM 输出质量
- **Embedding Provider 切换**: `ingestion.py` 和 `retrieval.py` 各自独立实现了 DashScope Embedding 调用，逻辑重复但不完全一致

## Safe First Tasks (Low Risk)

1. **环境检查脚本**: 编写 `scripts/check_env.py`，启动前验证 `.env` 中所有必需 Key 是否存在
2. **日志规范化**: 将 `ingestion.py` 中的 `print('11111111')` 等调试输出替换为 `logging`
3. **DashScope 结构化输出**: 改进 `BaseDashscopeProcessor.send_message` 使用 `json_repair` 解析 LLM 返回的 JSON，使其支持 `is_structured=True`
4. **Reranking 修复**: 修复 `reranking.py` 中 DashScope 分支硬编码 `relevance_score: 0.0` 的问题，实际解析 LLM 返回的评分
5. **Embedding 逻辑统一**: 将 `ingestion.py` 和 `retrieval.py` 中重复的 DashScope Embedding 调用抽取为共享工具函数

## Unknowns
- Docling 在 macOS ARM (Apple Silicon) 上的 GPU 加速支持状态
- `data/test_set/questions.json` 当前仅含 1 个问题（boolean 类型），`questions-1.json` 含更多问题，二者关系不明
- `subset.csv` 中有 21 家公司但仅 5 份 PDF，其余公司数据是否需要单独下载
- 竞赛完整数据集 `data/erc2_set/` 不包含 PDF，仅有问题和参考答案
- 项目之前在 Windows (PowerShell) 环境运行（见运行日志路径 `D:\RAG-Challenge-2-main`），切换到 macOS 后是否有路径兼容性问题
