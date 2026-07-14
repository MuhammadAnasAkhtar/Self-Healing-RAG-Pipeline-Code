import datetime
from typing import List, Dict, Any

class MetricsStore:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add(self, query: str, avg_relevance: float, top_k: int, healed: bool):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "avg_relevance": avg_relevance,
            "top_k": top_k,
            "healed": healed
        }
        self.history.append(entry)

    def get_all(self) -> List[Dict[str, Any]]:
        return self.history

    def clear(self):
        self.history = []