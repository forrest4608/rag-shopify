# RAG Microservice API Reference

This document provides a comprehensive guide to the endpoints exposed by the RAG Microservice. This API allows third-party services to seamlessly integrate with the enterprise knowledge base, query information dynamically, and upload new data without disrupting service availability.

## Base URL
When running the service locally using the CLI command `python main.py serve --port 8000`, the base URL is:
```text
http://127.0.0.1:8000
```

---

## 1. Query Endpoint
Retrieves an accurate answer to a specified question regarding a target company by leveraging the memory-resident Vector databases and LLM RAG pipelines.

**Endpoint:** `/query`  
**Method:** `POST`  
**Content-Type:** `application/json`

### Request Body
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `company_name` | `string` | Yes | - | The exact name of the company to query within the database (e.g., `"Holley Inc."`). |
| `question` | `string` | Yes | - | The natural language question you want to ask (e.g., `"What was Holley Inc.'s revenue?"`). |
| `schema_type` | `string` | No | `"number"` | The output schema hint for the LLM. Available options: `"number"`, `"boolean"`, `"name"`, `"names"`, `"comparative"`. |

#### Example Request
```bash
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
           "company_name": "Holley Inc.",
           "question": "What was Holley Inc.\'\''s revenue?",
           "schema_type": "number"
         }'
```

### Response
Returns a JSON object detailing the answer along with origin references.

| Field | Type | Description |
|---|---|---|
| `question_text` | `string` | The originally submitted question. |
| `company_name` | `string` | The target company queried. |
| `kind` | `string` | The schema type used for the query. |
| `value` | `string` | The final computed answer from the RAG pipeline. *Note: If using DashScope, this may include embedded JSON reasoning steps in markdown blocks.* |
| `references` | `array` | A list of objects containing the exact `pdf_sha1` and `page_index` (0-based) where the answer was extracted from. |
| `reasoning_process` | `string` | (Optional) Contains step-by-step reasoning analysis if provided separately by the internal OpenAi-compatible pipeline handler. |

#### Example Response
```json
{
  "question_text": "What was Holley Inc.'s revenue?",
  "company_name": "Holley Inc.",
  "kind": "number",
  "value": "```\n{\n  \"step_by_step_analysis\": \"...\",\n  \"final_answer\": 688415000\n}\n```",
  "references": [
    {
      "pdf_sha1": "194000c9109c6fa628f1fed33b44ae4c2b8365f4",
      "page_index": 35
    }
  ],
  "reasoning_process": ""
}
```

---

## 2. Document Ingestion Endpoint
Uploads a new PDF report to the system for a specified company. The API instantly writes the file and incrementally updates the knowledge base asynchronously in the background. Once the background process finishes parsing and generating vector embeddings, the memory-resident RAG indexes will seamlessly reload (Hot Reload) without any service downtime.

**Endpoint:** `/ingest`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

### Request Payload
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | `file` (PDF) | Yes | The actual `.pdf` document to be processed. |
| `company_name` | `string` | Yes | The name of the company the document belongs to. Used to associate metadata dynamically. |

#### Example Request
```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/local/Holley_Inc_Annual_Report_2023.pdf" \
     -F "company_name=Holley Inc."
```

### Response
Returns immediately once the upload is saved. The actual NLP parsing and vector chunking takes place securely in the background.

| Field | Type | Description |
|---|---|---|
| `status` | `string` | Typically `"success"` if the file was accepted. |
| `message` | `string` | Details indicating that the background task was dispatched. |

#### Example Response
```json
{
  "status": "success",
  "message": "Document Holley_Inc_Annual_Report_2023.pdf uploaded for Holley Inc.. Ingestion started in background."
}
```

---

## 3. Error Handling
All errors will return standard HTTP status codes along with a JSON body detailing the issue.
- `400 Bad Request`: When a non-PDF file is submitted to `/ingest`.
- `422 Unprocessable Entity`: Validation error caused by malformed request body parameters.
- `500 Internal Server Error`: For unexpected system failures, or if the RAG query engine fails to formulate a retrieval plan.
- `503 Service Unavailable`: If `/query` is invoked before the `RAGService` singleton finishes initializing during startup.

#### Example Error Payload
```json
{
  "detail": "Only PDF files are supported."
}
```
