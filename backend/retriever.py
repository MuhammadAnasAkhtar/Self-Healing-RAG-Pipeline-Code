import numpy as np
from typing import List
from backend.embeddings import Embedder
from backend.vector_store import VectorStore

class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        """Retrieve relevant chunks for a query."""
        query_emb = self.embedder.embed([query])[0]
        results = self.vector_store.search(query_emb, k=top_k)
        return results