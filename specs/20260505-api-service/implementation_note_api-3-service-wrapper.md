# Implementation Note

## Task
`api-3-service-wrapper` - Create `src/api/rag_service.py` to wrap `QuestionsProcessor` and `HybridRetriever`.

## Files Changed
- `src/api/rag_service.py` (New file)

## Why Each File Changed
- `src/api/rag_service.py`: Created a stateful class `RAGService` that initializes the retriever and models only once and keeps them in memory. In the original `QuestionsProcessor.get_answer_for_company`, the retriever was re-instantiated (which triggers reloading all FAISS indices from disk) for *every single question*. The new wrapper eliminates this overhead and allows for near real-time API query responses.
- Added a `reload_indices()` method to dynamically rebuild the in-memory retrieval index after incremental documents are ingested.

## Tests Run
- Created and executed a temporary test script `scratch/test_rag_service.py` pointing to the test FAISS databases.
- Successfully performed a live query: "What was Holley Inc.'s revenue?" 
- The query successfully executed and fetched the context, routing to DashScope API to generate the correct numeric answer (`688415000`) with references (`[36]`) seamlessly.

## Evals Run
- N/A

## Verification Result
- Singletons work perfectly. Memory stays persistent across method calls.

## Risks
- Low. The core `src/questions_processing.py` and `src/retrieval.py` files remain untouched to ensure CLI batch commands continue working precisely as before.

## Rollback Plan
- Delete `src/api/rag_service.py`.
