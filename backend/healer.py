from backend.config import settings
from typing import List, Dict, Any
import datetime

class HealingAction:
    def __init__(self, action: str, reason: str, details: Dict[str, Any] = None):
        self.timestamp = datetime.datetime.now().isoformat()
        self.action = action
        self.reason = reason
        self.details = details or {}

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "reason": self.reason,
            "details": self.details
        }

class Healer:
    def __init__(self):
        self.last_heal_time = None
        self.strategy_index = settings.HEALING_CURRENT_STRATEGY_INDEX

    def evaluate_and_heal(self, avg_score: float) -> List[HealingAction]:
        """
        Decide if healing is needed based on average relevance score.
        Returns list of healing actions taken.
        """
        actions = []
        now = datetime.datetime.now()
        if avg_score < settings.RELEVANCE_THRESHOLD:
            # Check cooldown
            if self.last_heal_time is not None:
                elapsed = (now - self.last_heal_time).total_seconds()
                if elapsed < settings.HEALING_COOLDOWN:
                    # Still in cooldown, skip healing
                    return actions

            # Perform healing
            strategy = settings.HEALING_STRATEGIES[self.strategy_index]
            action = self._apply_strategy(strategy)
            actions.append(action)
            # Cycle strategy for next time
            self.strategy_index = (self.strategy_index + 1) % len(settings.HEALING_STRATEGIES)
            settings.HEALING_CURRENT_STRATEGY_INDEX = self.strategy_index
            self.last_heal_time = now

        return actions

    def _apply_strategy(self, strategy: str) -> HealingAction:
        """Apply a specific healing strategy and return the action taken."""
        action_details = {}
        if strategy == "increase_chunk_size":
            old = settings.CHUNK_SIZE
            settings.CHUNK_SIZE = min(old * 2, 2048)
            action_details = {"old_chunk_size": old, "new_chunk_size": settings.CHUNK_SIZE}
            return HealingAction("increase_chunk_size", "Low relevance, trying larger chunks", action_details)
        elif strategy == "decrease_chunk_size":
            old = settings.CHUNK_SIZE
            settings.CHUNK_SIZE = max(old // 2, 128)
            action_details = {"old_chunk_size": old, "new_chunk_size": settings.CHUNK_SIZE}
            return HealingAction("decrease_chunk_size", "Low relevance, trying smaller chunks", action_details)
        elif strategy == "switch_embed_model":
            old = settings.EMBED_MODEL_NAME
            new = settings.ALTERNATE_EMBED_MODEL_NAME
            settings.EMBED_MODEL_NAME = new
            action_details = {"old_model": old, "new_model": new}
            # Also swap alternate for future switches
            settings.ALTERNATE_EMBED_MODEL_NAME = old
            return HealingAction("switch_embed_model", "Trying different embedding model", action_details)
        elif strategy == "reindex_with_sentence_chunking":
            old_strategy = settings.CHUNK_STRATEGY
            settings.CHUNK_STRATEGY = "sentence"
            action_details = {"old_strategy": old_strategy, "new_strategy": "sentence"}
            return HealingAction("reindex_with_sentence_chunking", "Switch to sentence-based chunking", action_details)
        else:
            return HealingAction("unknown", f"Unrecognized strategy: {strategy}")