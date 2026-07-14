from sentence_transformers import CrossEncoder
from typing import List
import numpy as np

class Judge:
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def score(self, query: str, chunks: List[str]) -> List[float]:
        """Score relevance of each chunk to the query. Returns list of scores (0-1)."""
        if not chunks:
            return []
        pairs = [[query, chunk] for chunk in chunks]
        scores = self.model.predict(pairs)
        # CrossEncoder outputs logits; we convert to [0,1] with sigmoid
        scores = 1 / (1 + np.exp(-np.array(scores)))
        return scores.tolist()

    def average_score(self, query: str, chunks: List[str]) -> float:
        """Return average relevance score."""
        scores = self.score(query, chunks)
        if not scores:
            return 0.0
        return float(np.mean(scores))