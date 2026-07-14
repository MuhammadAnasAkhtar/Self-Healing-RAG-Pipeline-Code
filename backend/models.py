from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    filename: str
    num_chunks: int
    message: str

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None

class RetrievedChunk(BaseModel):
    text: str
    score: float  # similarity score
    relevance: Optional[float] = None  # judge score

class HealingAction(BaseModel):
    timestamp: str
    action: str
    reason: str
    details: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    avg_relevance: float
    threshold: float
    healed: bool
    healing_actions: List[HealingAction] = []

class MetricsPoint(BaseModel):
    timestamp: str
    query: str
    avg_relevance: float
    top_k: int
    healed: bool

class MetricsResponse(BaseModel):
    history: List[MetricsPoint]

class ConfigUpdate(BaseModel):
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    embed_model_name: Optional[str] = None
    relevance_threshold: Optional[float] = None