"""Token budget + rate limit gate. Enforced per Streamlit session."""

import time
from collections import deque
from typing import Tuple


class RateLimiter:
    def __init__(self, max_messages: int = 20, window_seconds: int = 300):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._timestamps: deque = deque()

    def allow(self) -> Tuple[bool, int]:
        now = time.time()
        while self._timestamps and now - self._timestamps[0] > self.window_seconds:
            self._timestamps.popleft()
        if len(self._timestamps) >= self.max_messages:
            wait = int(self.window_seconds - (now - self._timestamps[0]))
            return False, wait
        self._timestamps.append(now)
        return True, 0


class TokenBudget:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.used = 0

    def remaining(self) -> int:
        return max(0, self.max_tokens - self.used)

    def can_spend(self, est: int = 0) -> bool:
        return self.used + est <= self.max_tokens

    def spend(self, tokens: int) -> None:
        self.used += max(0, tokens)


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return max(1, len(text) // 4)
