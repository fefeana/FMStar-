from typing import Any

from .l1_local import L1Cache
from .policy import PolicyEngine


class CacheManager:
    def __init__(self):
        self.l1 = L1Cache()
        self.policy = PolicyEngine()

    def get(self, key: str) -> Any:
        val = self.l1.get(key)
        if val is not None:
            return val
        return None

    def set(self, key: str, value: Any, size: int = 0, ttl: int = 3600) -> None:
        destination = self.policy.decide_storage(size, ttl)
        if destination == "L1":
            self.l1.set(key, value)
