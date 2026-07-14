from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Chunking – sentence-based with generous overlap
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 100
    CHUNK_STRATEGY: str = "sentence"

    # Strong embedding model
    EMBED_MODEL_NAME: str = "all-mpnet-base-v2"

    # Judge model
    JUDGE_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RELEVANCE_THRESHOLD: float = 0.25          # heal only when truly terrible

    # LLM for generation
    LLM_MODEL_NAME: str = "google/flan-t5-large"

    # Vector store
    VECTOR_DB_PATH: str = "data/vector_store"
    DATA_DIR: str = "data/documents"

    # Healing
    HEALING_COOLDOWN: int = 30
    TOP_K: int = 15                             # fetch more chunks
    HEALING_STRATEGIES: List[str] = [
        "increase_chunk_size",
        "decrease_chunk_size",
        "switch_embed_model",
        "reindex_with_sentence_chunking"
    ]
    HEALING_CURRENT_STRATEGY_INDEX: int = 0
    ALTERNATE_EMBED_MODEL_NAME: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()