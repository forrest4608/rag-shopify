# Project Map

## Project Type
RAG (Retrieval-Augmented Generation) Pipeline for analyzing and answering questions about company annual reports.

## Language/Framework/Runtime
- Python 3.11+

## Package Manager
- `pip` (Dependencies specified in `requirements.txt`)

## Main Directories
- `src/`: Core business logic, pipeline stages, and modules.
- `data/`: Datasets (test set, full ERC2 set).
- `tests/`: Automated test suite.
- `docs/`: Documentation and AI agent context.
- `evals/`: Evaluation scripts/results.

## Main Entry Points
- `main.py`: Command Line Interface (CLI) utilizing `click` for executing specific pipeline stages.
- `src/pipeline.py`: Core orchestration class `Pipeline` that strings together parsing, ingestion, retrieval, and generation.

## Configuration Files
- `.env`: API keys and environment variables.
- `setup.py`: Minimal setup script for local installation.

## External Dependencies
- **LLM/API Clients**: `openai`, `google-generativeai`, `tiktoken`, `google-api-python-client`
- **RAG & Search**: `faiss-cpu`, `rank-bm25`, `langchain`
- **Parsing & Data**: `docling`, `PyPDF2`, `pandas`, `json_repair`, `pydantic`
- **Utilities**: `aiohttp`, `requests`, `click`, `tqdm`, `python-dotenv`
