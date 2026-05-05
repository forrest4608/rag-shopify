from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import shutil
from pathlib import Path
import os
import pandas as pd
from contextlib import asynccontextmanager

from src.api.rag_service import RAGService
from src.pipeline import Pipeline, max_nst_o3m_config

# Global instances
rag_service: Optional[RAGService] = None
pipeline: Optional[Pipeline] = None
root_path: Path = Path.cwd() / "data" / "test_set"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service, pipeline
    print("Initializing RAG Service and Pipeline...")
    
    # Initialize pipeline
    # We use no_ser_tab because it's faster for MVP
    run_config = max_nst_o3m_config
    pipeline = Pipeline(root_path, run_config=run_config)
    
    # Initialize RAGService
    rag_service = RAGService(
        vector_db_dir=pipeline.paths.vector_db_dir,
        documents_dir=pipeline.paths.documents_dir,
        subset_path=pipeline.paths.subset_path,
        run_config=run_config
    )
    
    yield
    print("Shutting down RAG Service...")

app = FastAPI(title="RAG Microservice API", lifespan=lifespan)

class QueryRequest(BaseModel):
    company_name: str
    question: str
    schema_type: str = "number"

@app.post("/query")
async def query_rag(request: QueryRequest):
    """
    Answers a query using the RAG Service.
    """
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service is not initialized.")
        
    result = rag_service.answer_query(
        company_name=request.company_name,
        question=request.question,
        schema=request.schema_type
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

def run_ingestion_pipeline():
    """Background task to process new files and reload indices."""
    try:
        print("Running ingestion pipeline for new documents...")
        pipeline.parse_pdf_reports(parallel=True)
        pipeline.process_parsed_reports()
        print("Ingestion pipeline completed. Reloading RAG Service indices...")
        rag_service.reload_indices()
        print("Indices reloaded successfully.")
    except Exception as e:
        import traceback
        print(f"Error during ingestion pipeline: {e}\n{traceback.format_exc()}")

@app.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    company_name: str = Form(...)
):
    """
    Uploads a new PDF report for a company and triggers incremental ingestion in the background.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Save the file
    pdf_dir = pipeline.paths.pdf_reports_dir
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = pdf_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # Get SHA1 (filename stem)
    sha1 = file_path.stem
    
    # Update subset.csv
    subset_path = pipeline.paths.subset_path
    if subset_path.exists():
        df = pd.read_csv(subset_path)
        # Check if already exists
        if sha1 not in df['sha1'].values:
            # Create a new row with defaults
            new_row = {col: False for col in df.columns}
            new_row['sha1'] = sha1
            new_row['company_name'] = company_name
            new_row['cur'] = "USD"
            new_row['major_industry'] = "Unknown"
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(subset_path, index=False)
            print(f"Added {company_name} ({sha1}) to subset.csv")
    else:
        # Create minimal subset.csv
        df = pd.DataFrame([{"sha1": sha1, "company_name": company_name}])
        df.to_csv(subset_path, index=False)
        
    # Trigger pipeline
    background_tasks.add_task(run_ingestion_pipeline)
    
    return {
        "status": "success",
        "message": f"Document {file.filename} uploaded for {company_name}. Ingestion started in background."
    }
