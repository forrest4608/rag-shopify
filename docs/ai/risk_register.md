# Risk Register

## High-Risk Modules
- **`src/api_requests.py` & `src/reranking.py`**: These modules interact heavily with unpredictable LLM APIs. JSON parsing failures, rate limits, and schema hallucinations are frequent. Fallback mechanisms (like `json_repair` and regex) are brittle.
- **`src/pdf_parsing.py`**: Relies on Docling, which can be resource-intensive and fail unpredictably on poorly formatted PDFs.

## No-Test Areas
- Almost the entire RAG pipeline (Retrieval, Ingestion, API interactions) lacks unit tests. Any refactoring here carries high regression risk.

## Security-Sensitive Areas
- **API Keys**: Managed via `.env` file. Accidental commit of this file or leakage in logs is a risk. Ensure `.gitignore` is strictly respected.
- **Data Privacy**: If real company annual reports are processed using third-party APIs (OpenAI, DashScope), data governance and privacy policies must be considered.

## Unknowns
- Rate limits and concurrency thresholds for various API providers (especially DashScope/Qwen vs OpenAI).
- Behavior of the system on extremely large documents that exceed embedding or LLM context windows.
