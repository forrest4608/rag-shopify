# Security Review: API Service Transformation

## Iteration Details
- Iteration: `20260505-api-service`
- Date: 2026-05-05

## Security Domains Assessed

### 1. File Upload Risks
- **Threat**: The `/ingest` endpoint accepts `UploadFile`. Malicious payloads (e.g., non-PDF files or extremely large files) could exploit the ingestion service.
- **Mitigation**: Implemented basic `.pdf` suffix validation.
- **Risk Level**: **Medium**. (No strict MIME type validation or file-size restriction is implemented yet, though acceptable for internal MVP).

### 2. State & Memory Exhaustion
- **Threat**: Loading `HybridRetriever` directly into RAM limits scaling if thousands of files are incrementally ingested over time.
- **Mitigation**: The system is intended to be a monolithic container. Horizontal scaling is required for larger-scale production, which is beyond this scope.
- **Risk Level**: **Low**.

### 3. Execution Environment Risks
- **Threat**: `RAGService.reload_indices()` is triggered in a background task asynchronously. Thread-safety could be an issue if queries arrive exactly as the pointers are refreshing.
- **Mitigation**: Python's GIL and object replacement generally makes atomic swapping of `self.retriever = new_retriever` relatively safe.
- **Risk Level**: **Low**.

### 4. API Key & Secret Leaks
- **Threat**: Accidental leakage of `OPENAI_API_KEY` or `DASHSCOPE_API_KEY` via API logs.
- **Mitigation**: Secrets continue to be pulled explicitly from `.env` environment contexts and are not printed to error tracebacks via FastAPI.
- **Risk Level**: **None**.

## Final Security Assessment
The system conforms to standard internal microservice security postures. External-facing deployments will need rate-limiting and robust file upload sanitization before production launch.
**Security Decision: APPROVED.**
