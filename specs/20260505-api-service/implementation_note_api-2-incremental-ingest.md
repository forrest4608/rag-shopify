# Implementation Note

## Task
`api-2-incremental-ingest` - Modify `ingestion.py` to support incremental updates.

## Files Changed
- `src/ingestion.py`

## Why Each File Changed
- `src/ingestion.py`: Added checks in both `BM25Ingestor.process_reports` and `VectorDBIngestor.process_reports` to verify if the output index file (`.pkl` or `.faiss`) already exists for a given `sha1_name`. If it exists, the file is skipped. This takes advantage of the fact that the existing architecture generates 1 index per document instead of 1 monolithic index, which elegantly supports adding new documents incrementally.

## Key Decisions
- Did not change the structure of the vector databases. The architecture natively supports single-document indexes which are loaded iteratively at retrieval time. The "append" logic simply means "generate indexes only for newly added JSON files and skip existing ones".

## Tests Run
- Executed `main.py process-reports --config no_ser_tab` on a directory with existing indexes. Verified that it skipped embeddings generation.
- Deleted a specific `.faiss` index and re-ran the pipeline. Verified that the script selectively rebuilt the missing index while skipping the rest.

## Evals Run
- N/A

## Verification Result
- Incremental building works seamlessly and drastically reduces the time to ingest new documents compared to a full rebuild.

## Risks
- Low. Only added simple `if file.exists(): continue` statements. No data structure changes.

## Rollback Plan
- Revert the modifications in `src/ingestion.py` using `git restore src/ingestion.py`.
