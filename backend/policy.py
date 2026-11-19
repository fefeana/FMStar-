class PolicyEngine:
    def decide_storage(self, data_size: int, ttl: int) -> str:
        if data_size < 10_000 and ttl < 300:
            return "L1"
        return "L2"
