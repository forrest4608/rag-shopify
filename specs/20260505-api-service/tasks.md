# Tasks

## Task 1: Add API Dependencies
- **Task ID**: `api-1-deps`
- **Goal**: Add FastAPI and Uvicorn.
- **Acceptance criteria**: `pip install -r requirements.txt` succeeds and `import fastapi` works.
- **Files likely involved**: `requirements.txt`
- **Verification method**: Manual import check.
- **Risk level**: Low.

## Task 2: Implement Incremental Ingestion
- **Task ID**: `api-2-incremental-ingest`
- **Goal**: Modify `ingestion.py` to support appending to an existing FAISS index and updating `documents.json`.
- **Acceptance criteria**: Processing a new document adds it to the existing `vector_db` folder without deleting previous entries.
- **Files likely involved**: `src/ingestion.py`
- **Verification method**: Run ingestion twice with different documents and verify both exist in the index.
- **Risk level**: Medium (Data loss if overwrite logic is flawed).

## Task 3: Create RAG Service Wrapper
- **Task ID**: `api-3-service-wrapper`
- **Goal**: Create a stateful class that keeps `HybridRetriever` and `QuestionsProcessor` in memory and allows updating them dynamically.
- **Acceptance criteria**: Can instantiate the service once and answer multiple distinct questions without reloading FAISS.
- **Files likely involved**: `src/api/rag_service.py` (New), `src/retrieval.py` (minor updates for reload).
- **Verification method**: Unit test calling the service twice.
- **Risk level**: Low.

## Task 4: Implement FastAPI Endpoints & CLI command
- **Task ID**: `api-4-endpoints`
- **Goal**: Build `POST /api/v1/query` and `POST /api/v1/ingest` endpoints, and add `serve` to `main.py`.
- **Acceptance criteria**: `python main.py serve` starts the server. Endpoints respond correctly to HTTP requests.
- **Files likely involved**: `src/api/server.py` (New), `main.py`.
- **Verification method**: Send requests via `curl` or FastAPI Swagger UI.
- **Risk level**: Low.
