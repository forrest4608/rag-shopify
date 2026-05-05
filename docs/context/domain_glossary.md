# Domain Glossary

## Business Terms
- **RAG (Retrieval-Augmented Generation)**: Architecture that augments LLM prompts with external retrieved data.
- **Reranking**: A secondary sorting phase where an LLM or cross-encoder re-evaluates retrieved chunks for relevance to the specific query.
- **Parent Document Retrieval**: A retrieval strategy where small chunks are indexed for search, but larger surrounding parent chunks are retrieved for context.
- **Table Serialization**: The process of converting complex PDF tables into a flattened JSON or textual representation that LLMs can easily read.

## Entities
- **Report / Annual Report**: The primary source PDF document for a specific company and year.
- **Question**: A user query, which may target a single company or require cross-company comparison.
- **Chunk / Block**: A segmented portion of text from a report, used for granular vector search.
- **Relevance Score**: A metric (0.0 to 1.0) indicating how well a chunk answers a question.

## States
- **Parsed**: PDF converted to structured data.
- **Embedded**: Text converted to vector embeddings.
- **Reranked**: Documents sorted by relevance score using an LLM.
- **Answered**: Question fulfilled with an LLM-generated response.

## Workflows
- **Parse PDFs**: Convert PDFs to JSON representations.
- **Serialize Tables**: Process tables within JSON.
- **Process Reports**: Build Faiss/BM25 indexes from processed JSON.
- **Process Questions**: Answer test queries using the indexes.

## Rules
- **JSON Schema Output**: All LLM outputs must strictly adhere to predefined JSON schemas (defined in `src/prompts.py`).
- **N/A Fallback**: If information is not present in the retrieved context, the LLM must explicitly output "N/A" according to the schema.
