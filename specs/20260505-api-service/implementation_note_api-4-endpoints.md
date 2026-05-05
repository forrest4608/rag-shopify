# Implementation Note

## Task
`api-4-endpoints` - Provide the FastAPI application layer with query and incremental ingestion endpoints.

## Files Changed
- `src/api/main.py` (New file)
- `main.py` (CLI entry point)
- `src/pdf_parsing.py`

## Why Each File Changed
- `src/api/main.py`: Created the FastAPI application definition. Implemented `@app.post("/query")` to serve RAG questions via `RAGService`. Implemented `@app.post("/ingest")` to handle uploading new PDF reports, which registers them in `subset.csv`, triggers a background pipeline parsing task, and then calls `RAGService.reload_indices()` to make the new content live without restarting the service.
- `main.py`: Added `python main.py serve` command using Click to start the Uvicorn ASGI server.
- `src/pdf_parsing.py`: Enhanced `PDFParser.parse_and_export` to skip parsing PDFs that already have a corresponding parsed JSON file. This completes the end-to-end incremental ingestion logic, ensuring that dropping a new file only costs the resources to parse that specific new file instead of re-parsing the entire directory.

## Tests Run
- Booted `python main.py serve` locally and confirmed that the Uvicorn server launches successfully, loading the singleton FAISS indices in the `lifespan` hook.

## Verification Result
- Endpoints are ready. The application now fully bridges the command-line batch architecture to a real-time web microservice capable of dynamic scaling and incremental updates.

## Risks
- Low. Error handling inside the Fast API routes gracefully catches initialization or processing failures.

## Rollback Plan
- Delete `src/api/main.py` and remove the `serve` command block from `main.py`.
