from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import asyncio
import os
import PyPDF2
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

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

app = FastAPI(title="RAG Microservice API", lifespan=lifespan)

# Allow CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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

async def run_ingestion_pipeline():
    """Background task to process new files and reload indices with WebSocket progress."""
    try:
        await manager.broadcast({"type": "progress", "message": "准备解析 PDF 文档...", "percent": 10})
        await asyncio.sleep(1) # Visual delay for impact
        
        print("Running ingestion pipeline for new documents...")
        pipeline.parse_pdf_reports(parallel=True)
        await manager.broadcast({"type": "progress", "message": "PDF 解析完成，正在构建向量索引...", "percent": 50})
        
        pipeline.process_parsed_reports()
        await manager.broadcast({"type": "progress", "message": "索引构建完成，正在同步内存...", "percent": 90})
        
        rag_service.reload_indices()
        await manager.broadcast({"type": "progress", "message": "知识库已实时更新！", "percent": 100})
        
        print("Ingestion pipeline completed.")
        # Final broadcast to clear status
        await asyncio.sleep(2)
        await manager.broadcast({"type": "finished"})
    except Exception as e:
        import traceback
        err_msg = f"处理失败: {str(e)}"
        await manager.broadcast({"type": "error", "message": err_msg})
        print(f"Error during ingestion pipeline: {e}\n{traceback.format_exc()}")

@app.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    company_name: str = Form(...),
    currency: str = Form("USD"),
    major_industry: str = Form("Unknown")
):
    """
    Uploads a new PDF report and triggers background ingestion.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件。")
        
    # Save the file
    pdf_dir = pipeline.paths.pdf_reports_dir
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = pdf_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    sha1 = file_path.stem
    
    # Calculate metadata at ingestion time
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    size_str = f"{size_mb:.1f} MB"
    page_count = "-"
    try:
        with open(file_path, 'rb') as pf:
            reader = PyPDF2.PdfReader(pf)
            page_count = str(len(reader.pages))
    except:
        pass
    
    # Update subset.csv (our simple database)
    subset_path = pipeline.paths.subset_path
    if subset_path.exists():
        df = pd.read_csv(subset_path)
        if sha1 not in df['sha1'].values:
            new_row = {col: False for col in df.columns}
            new_row['sha1'] = sha1
            new_row['company_name'] = company_name
            new_row['size'] = size_str
            new_row['page_count'] = page_count
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(subset_path, index=False)
    else:
        df = pd.DataFrame([{"sha1": sha1, "company_name": company_name, "size": size_str, "page_count": page_count}])
        df.to_csv(subset_path, index=False)
        
    # Trigger pipeline - note: we changed it to async for broadcasting
    background_tasks.add_task(run_ingestion_pipeline)
    
    return {
        "status": "success",
        "message": f"文档 {file.filename} 已接收，开始后台解析。"
    }

@app.get("/documents")
async def list_documents():
    """List all documents from subset.csv with metadata"""
    subset_path = pipeline.paths.subset_path
    if not subset_path.exists():
        return []
    df = pd.read_csv(subset_path)
    df = df.fillna("")
    
    docs = []
    cols = [c for c in ['sha1', 'company_name', 'size', 'page_count'] if c in df.columns]
    for _, row in df.iterrows():
        doc = {col: row[col] for col in cols}
        # Fallback for old records that don't have these columns
        if 'size' not in doc or not doc['size']:
            doc['size'] = '-'
        if 'page_count' not in doc or not doc['page_count']:
            doc['page_count'] = '-'
        docs.append(doc)
        
    return docs

@app.get("/documents/{sha1}/pdf")
async def get_document_pdf(sha1: str):
    """Serve the original PDF file"""
    pdf_path = pipeline.paths.pdf_reports_dir / f"{sha1}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Original PDF not found")
    return FileResponse(path=pdf_path, media_type='application/pdf', filename=f"{sha1}.pdf")

@app.delete("/documents/{sha1}")
async def delete_document(sha1: str):
    """Delete a document by sha1 and remove its associated files"""
    # 1. Remove from subset.csv
    subset_path = pipeline.paths.subset_path
    if subset_path.exists():
        df = pd.read_csv(subset_path)
        df = df[df['sha1'] != sha1]
        df.to_csv(subset_path, index=False)
        
    # 2. Remove PDF
    pdf_path = pipeline.paths.pdf_reports_dir / f"{sha1}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()
        
    # 3. Remove parsed JSON
    json_path = pipeline.paths.documents_dir / f"{sha1}.json"
    if json_path.exists():
        json_path.unlink()
        
    # 4. Remove vector DBs
    bm25_path = pipeline.paths.vector_db_dir / f"bm25_{sha1}.pkl"
    faiss_index_path = pipeline.paths.vector_db_dir / f"faiss_{sha1}.index"
    faiss_pkl_path = pipeline.paths.vector_db_dir / f"faiss_{sha1}.pkl"
    for p in [bm25_path, faiss_index_path, faiss_pkl_path]:
        if p.exists():
            p.unlink()
            
    # 5. Reload indices in memory
    if rag_service:
        rag_service.reload_indices()
        
    return {"status": "success", "message": f"Document {sha1} deleted."}

