# Iteration Brief

## Problem
The current RAG pipeline is a CLI-based batch processing tool. It requires running scripts to process entire datasets and lacks real-time interaction capabilities. Furthermore, adding new documents requires a full re-indexing of the dataset.

## Target User
Developers and downstream applications that need to interact with the RAG system programmatically.

## User Scenario
1. A developer sends a JSON request to an API endpoint with a question about a company and receives the RAG-generated answer in real-time.
2. A system administrator uploads a newly released annual report via an API endpoint. The system processes the PDF and adds its chunks to the existing vector database incrementally, making it immediately available for querying without rebuilding the entire database.

## Business Value
Transforms the project from a static data analysis script into an interactive, deployable microservice, unlocking integration with web frontends, chat interfaces, and automated document ingestion pipelines.

## Success Metrics
- API responds to queries successfully.
- Incremental ingestion successfully adds a new document and allows subsequent queries to retrieve its content.
- Core architecture (retrieval logic, prompts) remains unchanged.

## Constraints
- Do not rewrite the core RAG logic (Docling parsing, LLM reranking, Qwen integration).
- Minimal architectural changes; wrap existing components.

## Non-goals
- Full authentication/authorization layer (keep it simple for now).
- Complex task queues (e.g., Celery) for background ingestion; synchronous or simple async processing is acceptable for the MVP.

## Open Questions
- The current BM25 implementation (`rank-bm25`) is static. We may need to rebuild the BM25 index on every incremental update, whereas FAISS can be appended to.

## Recommended Scope
- Introduce FastAPI for the API layer.
- Add 2 endpoints: `POST /api/v1/query` and `POST /api/v1/ingest`.
- Refactor `src/ingestion.py` to support incremental additions to FAISS and rebuilding of BM25.
