from typing import Optional

import aioredis
from aioredis import Redis

from api.config import settings


class Cache:
    def __init__(self, url, ttl):
        self.ttl = ttl
        self.url = url
        self.redis_cache: Optional[Redis] = None

    async def start(self):
        self.redis_cache = await aioredis.from_url(self.url, db=0, encoding="utf-8")

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, value, ex=self.ttl)

    async def get(self, key):
        value = await self.redis_cache.get(key)
        return value

    async def stop(self):
        if self.redis_cache is not None:
            await self.redis_cache.close()


cache = Cache(url=settings.redis_url, ttl=settings.redis_ttl)
