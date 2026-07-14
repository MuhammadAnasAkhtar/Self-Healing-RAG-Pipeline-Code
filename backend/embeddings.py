from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from backend.config import settings

class Embedder:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBED_MODEL_NAME
        self.model = SentenceTransformer(self.model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts, show_progress_bar=False)

    def switch_model(self, new_model_name: str):
        """Switch to a different embedding model."""
        self.model_name = new_model_name
        self.model = SentenceTransformer(new_model_name)