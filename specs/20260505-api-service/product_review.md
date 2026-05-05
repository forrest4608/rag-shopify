# Product Review

## User Value
High. Moving to a microservice architecture is a necessary step for production deployment and user interaction.

## MVP Scope
Appropriately scoped. Adding an API layer and modifying the ingestion script to handle appends rather than overwrites is the minimal viable path to achieving the goal.

## Non-goals
Clearly defined. Avoiding complex async queues and auth keeps the iteration focused on the core goal.

## Acceptance Criteria
- [ ] `FastAPI` is integrated and starts a web server.
- [ ] `POST /api/v1/query` accepts `{"company_name": "...", "query": "..."}` and returns the generated answer.
- [ ] `POST /api/v1/ingest` accepts a PDF file upload, processes it, and updates the vector indices.
- [ ] After ingestion, a query regarding the new PDF returns a correct answer.

## Decision
**Approved.** The iteration brief is clear, achievable, and provides significant value.
