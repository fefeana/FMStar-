from collections import OrderedDict
from typing import Any


class L1Cache:
    def __init__(self, capacity: int = 100):
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> Any:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
