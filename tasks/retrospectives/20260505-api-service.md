# Retrospective: 20260505-api-service

## Iteration Overview
- **Goal:** Transform a CLI-based batch processing RAG application into a microservice via FastAPI.
- **Result:** Successfully built a persistent `RAGService` wrapper, added `/query` and `/ingest` HTTP endpoints, and introduced an incremental processing logic.

## Analysis

### What worked
- Relying on the file system (`if file.exists(): continue`) to implement incremental ingestion was extremely efficient and avoided adding complex tracking databases.
- Creating a wrapper (`RAGService`) instead of aggressively refactoring `QuestionsProcessor` maintained backward compatibility for CLI commands.

### What failed
- Test verification stalled because test scripts assumed dummy data (`1C` company) that did not exist in the mock dataset (`subset.csv`).
- There was initial confusion around the API output formats (OpenAI dictionary vs DashScope raw markdown) because of external environment configurations set by the user.

### Where AI helped
- AI successfully analyzed the nested execution flow to trace why `VectorRetriever` was reloading the FAISS databases sequentially, identifying the exact bottleneck required to solve the task.

### Where AI was risky
- The AI initially bypassed strict verification of the external model's return schema when switching between `openai` and `dashscope` API clients, leading to a mismatched JSON response in the API output.

### Missed requirements
- None.

### Bugs found late
- DashScope's native API wrapper does not parse JSON into dict format, unlike the OpenAI interface.

### Over-engineering
- Did not over-engineer; avoided refactoring `Pipeline.process_reports()` by instead introducing the `RAGService` isolation layer.

### Under-testing
- None. Ran end-to-end curl and python testing directly on the live port.

### Missing evals
- None (Behavior remained untouched).

## New rules to add
- **Data Reality Check**: Ensure mock data used in verification scripts directly reflects the current local context (`subset.csv`) before testing.
- **Provider Parity Check**: When testing LLM routing, verify the exact return schema logic for the chosen API provider config, as wrappers behave differently.

## Next iteration recommendation
- Implement file-size limiting and strict MIME type checking for the `/ingest` route.
- Implement token-bucket rate-limiting for the `/query` endpoint.
