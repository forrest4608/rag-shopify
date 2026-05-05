# Architecture Map

## Main Modules
- **`src/pipeline.py`**: Orchestrates the overall workflow. Defines `RunConfig` presets and the `Pipeline` class.
- **`src/pdf_parsing.py`**: Uses Docling to parse raw PDF reports into structured JSON.
- **`src/tables_serialization.py`**: Extracts and serializes tables from parsed reports into text formats optimized for LLMs.
- **`src/parsed_reports_merging.py`**: Merges parsed text and tables into unified documents.
- **`src/text_splitter.py`**: Splits documents into manageable chunks for vectorization.
- **`src/ingestion.py`**: Embeds chunks and ingests them into vector databases (Faiss) and keyword indexes (BM25).
- **`src/retrieval.py`**: Handles hybrid search (Vector + BM25) and parent document retrieval.
- **`src/reranking.py`**: LLM-based reranking logic to score and sort retrieved chunks.
- **`src/api_requests.py` & `src/api_request_parallel_processor.py`**: Manages API calls to OpenAI, DashScope (Qwen), Gemini, etc., including rate limiting, retries, and JSON repair fallbacks.
- **`src/questions_processing.py`**: Handles query routing, context building, and final answer generation.
- **`src/prompts.py`**: Central repository for system prompts and Pydantic schemas.

## Module Responsibilities
The system follows a sequential pipeline architecture:
1. **Data Prep**: `pdf_parsing` -> `tables_serialization` -> `parsed_reports_merging`.
2. **Indexing**: `text_splitter` -> `ingestion`.
3. **Serving**: `questions_processing` calls `retrieval` -> `reranking` -> `api_requests`.

## Key Data Flows
- **Ingestion Flow**: PDF Report -> Parsed JSON -> Text Chunks -> Embeddings -> FAISS Index.
- **Query Flow**: User Question -> Retrieve Top N Chunks -> LLM Reranking -> Top K Chunks -> Construct Context -> LLM Generation -> Final Answer.

## Key API Boundaries
- External LLM Providers (OpenAI, DashScope/Qwen, Gemini) accessed via `api_requests.py`.
- Docling models for local document layout analysis.
- Local FAISS for vector storage.
