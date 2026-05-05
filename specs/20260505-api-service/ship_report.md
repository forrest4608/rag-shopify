# Ship Report: API Service Transformation

## Iteration
`20260505-api-service`

## Summary of Changes
This release transitions the batch RAG pipeline to a real-time HTTP API service. It implements a persistent wrapper that maintains embeddings in memory to eliminate reloading latency, adds endpoints for querying and incremental PDF ingestion, and modifies the ingestion logic to intelligently skip previously processed data.

## Changed Files
1. `requirements.txt`: Added FastAPI dependencies.
2. `src/ingestion.py`: Added "skip-if-exists" incremental logic for BM25 and Vector DBs.
3. `src/pdf_parsing.py`: Added incremental skip logic for PDF text parsing.
4. `src/api/rag_service.py` (New): Stateful class `RAGService` for memory-resident retrievers.
5. `src/api/main.py` (New): FastAPI application and routes (`/query`, `/ingest`).
6. `main.py`: Added `@cli.command() serve` to launch Uvicorn.

## Verification
- Dependency builds tested.
- Incremental building validated (skipped existing FAISS index successfully).
- RAGService dynamically fetched correct numerical answers without reloading the index.
- FastAPI Server booted locally without errors.

## Remaining Risks
1. **Upload Sanitation**: The `/ingest` route lacks robust file safety checks (only validates suffix).
2. **Horizontal Scaling**: Vector indices are locally cached. Multi-node load balancing would cause cache inconsistencies.

## Rollback Plan
If deployment fails or causes critical errors, rollback by checking out the main branch to revert modified files (`main.py`, `src/pdf_parsing.py`, `src/ingestion.py`), and delete the `src/api/` folder.

## Recommended Commit Message
```text
feat: Microservice Transformation and Incremental Ingestion API

- Added FastAPI application with `/query` and `/ingest` endpoints
- Implemented `RAGService` to keep FAISS and BM25 retrievers in-memory
- Refactored `VectorDBIngestor`, `BM25Ingestor`, and `PDFParser` to support incremental ingestion (skipping existing files)
- Appended FastAPI dependencies to requirements
- Exposed `serve` CLI command via Uvicorn
```
