import json

from redis import Redis


class Cache:
    def __init__(self, redis):
        self.redis_cache: Redis = redis

    @classmethod
    def initialize(cls):
        return cls(Redis(host="redis", port=6379, db=0, encoding="utf-8"))

    def set(self, key, value):
        return self.redis_cache.set(key, json.dumps(value))

    def get(self, key):
        return json.loads(self.redis_cache.get(key))
