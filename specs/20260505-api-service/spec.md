# Specification

## User Stories
1. As an API client, I want to send a POST request with a query and company name so that I can get a real-time answer from the RAG system.
2. As a system admin, I want to upload a PDF report via a POST request so that the knowledge base is updated incrementally without downtime or full rebuilds.

## Functional Requirements
1. **API Server**: A FastAPI application exposing endpoints.
2. **Query Endpoint (`/api/v1/query`)**:
   - Input: JSON `{"company": "...", "query": "..."}`
   - Output: JSON `{"answer": "...", "references": [...]}`
3. **Ingest Endpoint (`/api/v1/ingest`)**:
   - Input: Multipart form data (PDF file).
   - Output: JSON `{"status": "success", "message": "...", "chunks_added": int}`
4. **Incremental Ingestion**:
   - The system must append new embeddings to the existing FAISS index (`faiss.IndexFlatIP.add`).
   - The system must append the new chunks to the JSON document store and rebuild the BM25 index.

## Acceptance Criteria
- The server starts with `python main.py serve`.
- Query endpoint works using the existing `RunConfig` and Qwen model.
- Ingest endpoint works and the newly ingested data is immediately searchable.

## Edge Cases
- Querying a company that has no documents ingested.
- Uploading a non-PDF file.
- Uploading a PDF that fails Docling parsing.

## Error States
- 400 Bad Request for invalid JSON or file types.
- 500 Internal Server Error if the LLM API fails.

## Data Inputs
- JSON payloads for queries.
- File uploads for ingestion.

## Data Outputs
- JSON responses containing answers or status messages.

## Non-goals
- Authentication.
- Advanced background task queues.
