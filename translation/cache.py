from redis import Redis


class Cache:
    def __init__(self, redis: Redis, ttl: int):
        self.ttl: int = ttl
        self.redis_cache: Redis = redis

    @classmethod
    def initialize(cls, url: str, ttl: int):
        return cls(Redis.from_url(url, db=0, encoding="utf-8"), ttl=ttl)

    def set(self, key: str, value: str):
        return self.redis_cache.set(key, value, ex=self.ttl)

    def get(self, key: str):
        return self.redis_cache.get(key)
