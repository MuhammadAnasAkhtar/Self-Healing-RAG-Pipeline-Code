import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, dimension: int, index_path: str = None):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # inner product for cosine after normalization
        self.metadata: List[Dict[str, Any]] = []
        self.index_path = index_path

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]]):
        """Add embeddings and their metadata. Assumes embeddings are normalized."""
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: {embeddings.shape[1]} vs {self.dimension}")
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(metadatas)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search top-k similar vectors."""
        if len(self.metadata) == 0:
            return []
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append({
                    "text": self.metadata[idx]["text"],
                    "score": float(dist),
                    "metadata": self.metadata[idx]
                })
        return results

    def save(self, path: str):
        """Save index and metadata."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.meta", "wb") as f:
            pickle.dump(self.metadata, f)

    @classmethod
    def load(cls, path: str, dimension: int):
        """Load index and metadata."""
        index = faiss.read_index(f"{path}.index")
        with open(f"{path}.meta", "rb") as f:
            metadata = pickle.load(f)
        store = cls(dimension)
        store.index = index
        store.metadata = metadata
        return store

    @property
    def size(self):
        return self.index.ntotal