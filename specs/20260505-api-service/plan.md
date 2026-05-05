# Technical Plan

## Current System Context
The current system operates via a batch processing `Pipeline` class. Resources (like FAISS indices and BM25 models) are loaded from disk when a process starts, and queries are evaluated in a loop over a static dataset.

## Recommended Approach
1. **Dependency Addition**: Add `fastapi` and `uvicorn` to `requirements.txt`.
2. **Stateful Service**: Create a new class `RAGService` that initializes the `Pipeline` (or its sub-components like `HybridRetriever` and `QuestionsProcessor`) once and keeps them in memory.
3. **Incremental Ingestion (`src/ingestion.py`)**:
   - Modify the ingestion script to check if a vector DB exists. If yes, load it, generate embeddings for *only* the new documents, and append them.
   - For BM25, append the new documents to the local `documents.json` store and re-initialize the `BM25Okapi` object in memory.
4. **API Layer (`src/api/server.py`)**: Define the FastAPI app and endpoints.
5. **CLI Integration**: Add a `serve` command to `main.py` using `click` to start the Uvicorn server.

## Files Likely Changed
- `requirements.txt`
- `main.py`
- `src/ingestion.py`
- `src/retrieval.py` (to support reloading/updating indices in memory)
- `src/api/server.py` (New)
- `src/api/routes.py` (New)

## Data Model Changes
No changes to the schema of vector DB or chunk structures. Only changes to how they are updated (append vs overwrite).

## Test Strategy
- Use `fastapi.testclient.TestClient` to test the API endpoints.
- Create a test script `tests/test_api.py` to verify ingestion and querying.

## Rollback Plan
Revert changes to `main.py` and `src/ingestion.py`. Drop the newly added endpoints. Remove FastAPI from requirements.

## Risks
- **Concurrency**: The current code might not be thread-safe. `FastAPI` handles requests concurrently. Since FAISS search is generally thread-safe, it should be fine, but we must ensure we don't mutate state during a read.
- **Memory**: Rebuilding BM25 in memory during an ingestion request will consume CPU and memory, briefly blocking other operations if not handled carefully.

## Alternatives Considered
- Creating a separate microservice that calls the CLI via subprocess. (Rejected: Too slow, no shared memory).
