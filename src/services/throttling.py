import time
from typing import Dict, Tuple

class Throttler:
    def __init__(self) -> None:
        self._store: Dict[str, int] = {}

    def _key(self, user_id: int, action: str) -> str:
        return f"{user_id}:{action}"

    def check(self, user_id: int, action: str, min_interval_sec: int) -> Tuple[bool, int]:
        """
        Returns (allowed, retry_after).
        If not allowed, retry_after is seconds remaining.
        """
        now = int(time.time())
        k = self._key(user_id, action)
        last = self._store.get(k)
        if last is None or now - last >= min_interval_sec:
            self._store[k] = now
            return True, 0
        retry_after = min_interval_sec - (now - last)
        return False, retry_after

    def reset(self, user_id: int, action: str) -> None:
        self._store.pop(self._key(user_id, action), None)