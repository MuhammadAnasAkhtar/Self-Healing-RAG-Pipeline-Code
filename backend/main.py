from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
import os
import shutil
from typing import List
from backend.config import settings
from backend.models import (
    DocumentUploadResponse, QueryRequest, QueryResponse,
    MetricsResponse, ConfigUpdate
)
from backend.pipeline import Pipeline
from backend.vector_store import VectorStore  # Added for reset
from backend.retriever import Retriever        # Added for reset

app = FastAPI(title="Self-Healing RAG Pipeline", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Initialize pipeline
pipeline = Pipeline()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    # Save to temp
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Index
        num_chunks = pipeline.index_document(temp_path)
        return DocumentUploadResponse(
            filename=file.filename,
            num_chunks=num_chunks,
            message="Document indexed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/reset")
async def reset_knowledge_base():
    """Clear all indexed documents and vector store."""
    try:
        pipeline.vector_store = VectorStore(dimension=pipeline.dim)
        pipeline.retriever = Retriever(pipeline.embedder, pipeline.vector_store)
        pipeline.current_documents = []
        # Save empty store
        pipeline.vector_store.save(pipeline.vector_store_path)
        pipeline.metrics.clear()
        return {"status": "ok", "message": "Knowledge base cleared. Upload a new document to start fresh."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag(payload: QueryRequest):
    try:
        result = pipeline.query(payload.query, payload.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    history = pipeline.metrics.get_all()
    return MetricsResponse(history=history)

@app.get("/config")
async def get_config():
    return {
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "embed_model_name": settings.EMBED_MODEL_NAME,
        "relevance_threshold": settings.RELEVANCE_THRESHOLD,
        "chunk_strategy": settings.CHUNK_STRATEGY,
        "healing_cooldown": settings.HEALING_COOLDOWN,
        "top_k": settings.TOP_K,
    }

@app.post("/config")
async def update_config(config: ConfigUpdate):
    if config.chunk_size is not None:
        settings.CHUNK_SIZE = config.chunk_size
    if config.chunk_overlap is not None:
        settings.CHUNK_OVERLAP = config.chunk_overlap
    if config.embed_model_name is not None:
        settings.EMBED_MODEL_NAME = config.embed_model_name
        pipeline.embedder.switch_model(config.embed_model_name)
        dummy_emb = pipeline.embedder.embed(["test"])[0]
        new_dim = dummy_emb.shape[0]
        pipeline.dim = new_dim
        pipeline.vector_store = VectorStore(dimension=new_dim)
        pipeline.retriever = Retriever(pipeline.embedder, pipeline.vector_store)
        pipeline.reindex_all()
    if config.relevance_threshold is not None:
        settings.RELEVANCE_THRESHOLD = config.relevance_threshold
    return {"status": "ok"}

@app.post("/heal")
async def manual_heal():
    if pipeline.metrics.history:
        last_avg = pipeline.metrics.history[-1]["avg_relevance"]
        actions = pipeline.healer.evaluate_and_heal(last_avg)
        if actions:
            pipeline.reindex_all()
            return {"healed": True, "actions": [a.to_dict() for a in actions]}
    return {"healed": False, "message": "No healing needed or no prior metrics"}

@app.get("/documents")
async def list_documents():
    return {"documents": pipeline.current_documents}