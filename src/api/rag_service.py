from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import json

from src.retrieval import HybridRetriever, VectorRetriever
from src.questions_processing import QuestionsProcessor
from src.pipeline import RunConfig

class RAGService:
    """
    A stateful wrapper for the RAG pipeline components.
    Maintains vector databases and models in memory to serve API requests quickly.
    """
    def __init__(self, vector_db_dir: Path, documents_dir: Path, subset_path: Path, run_config: RunConfig):
        self.vector_db_dir = vector_db_dir
        self.documents_dir = documents_dir
        self.subset_path = subset_path
        self.run_config = run_config
        
        # Load QuestionsProcessor once
        self.processor = QuestionsProcessor(
            vector_db_dir=self.vector_db_dir,
            documents_dir=self.documents_dir,
            subset_path=self.subset_path,
            new_challenge_pipeline=True,
            parent_document_retrieval=self.run_config.parent_document_retrieval,
            llm_reranking=self.run_config.llm_reranking,
            llm_reranking_sample_size=self.run_config.llm_reranking_sample_size,
            top_n_retrieval=self.run_config.top_n_retrieval,
            api_provider=self.run_config.api_provider,
            answering_model=self.run_config.answering_model,
            full_context=self.run_config.full_context
        )
        
        # Keep a persistent retriever instance to avoid reloading FAISS on every query
        self.retriever = self._build_retriever()
        
    def _build_retriever(self):
        print("Loading FAISS indices into memory...")
        if self.run_config.llm_reranking:
            return HybridRetriever(
                vector_db_dir=self.vector_db_dir,
                documents_dir=self.documents_dir,
                reranking_provider=self.run_config.api_provider,
                reranking_model=self.run_config.answering_model
            )
        else:
            return VectorRetriever(
                vector_db_dir=self.vector_db_dir,
                documents_dir=self.documents_dir
            )

    def reload_indices(self):
        """Reload the vector and document indices after incremental ingestion."""
        print("Reloading retriever indices...")
        self.retriever = self._build_retriever()
        
    def answer_query(self, company_name: str, question: str, schema: str = "number") -> Dict[str, Any]:
        """
        Answers a single question by using the persistent retriever.
        """
        try:
            if self.run_config.full_context:
                retrieval_results = self.retriever.retrieve_all(company_name)
            else:
                # Need to unwrap the vector_retriever if it's HybridRetriever to access retrieve_by_company_name directly
                # Wait, HybridRetriever also has retrieve_by_company_name!
                retrieval_results = self.retriever.retrieve_by_company_name(
                    company_name=company_name,
                    query=question,
                    llm_reranking_sample_size=self.run_config.llm_reranking_sample_size,
                    top_n=self.run_config.top_n_retrieval,
                    return_parent_pages=self.run_config.parent_document_retrieval
                )
            
            if not retrieval_results:
                return {"error": "No relevant context found"}
                
            rag_context = self.processor._format_retrieval_results(retrieval_results)
            answer_dict = self.processor.openai_processor.get_answer_from_rag_context(
                question=question,
                rag_context=rag_context,
                schema=schema,
                model=self.processor.answering_model
            )
            
            # Post-process references
            pages = answer_dict.get("relevant_pages", [])
            validated_pages = self.processor._validate_page_references(pages, retrieval_results)
            answer_dict["relevant_pages"] = validated_pages
            
            try:
                raw_refs = self.processor._extract_references(validated_pages, company_name)
                # Convert page indices to 0-based for output standardization
                formatted_refs = [
                    {
                        "pdf_sha1": ref["pdf_sha1"],
                        "page_index": max(0, ref["page_index"] - 1)
                    }
                    for ref in raw_refs
                ]
            except Exception as e:
                formatted_refs = []
                print(f"Failed to extract references: {e}")
                
            value = answer_dict.get("final_answer")
            if value == "N/A":
                formatted_refs = []
                
            return {
                "question_text": question,
                "company_name": company_name,
                "kind": schema,
                "value": value,
                "references": formatted_refs,
                "reasoning_process": answer_dict.get("step_by_step_analysis")
            }
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"Error answering query: {e}\n{tb}")
            return {"error": str(e), "traceback": tb}
