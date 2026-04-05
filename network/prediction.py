"""
ChampCom Network Prediction - Client-side prediction and rollback
"""
from collections import deque


class Prediction:
    """Stores snapshot history for client-side prediction and rollback."""

    def __init__(self, max_history=32):
        self.history = deque(maxlen=max_history)

    def push(self, snapshots):
        self.history.append(snapshots)

    def rollback(self, frames):
        """Get the state from N frames ago."""
        if frames < len(self.history):
            return self.history[len(self.history) - 1 - frames]
        return []

    def latest(self):
        return self.history[-1] if self.history else []

    def clear(self):
        self.history.clear()

    def frame_count(self):
        return len(self.history)
