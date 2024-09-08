from common.storages.cache.interfaces import ICacheStorage
from redis.asyncio import Redis

class RedisCacheStorage(ICacheStorage):
    
    def __init__(self, redis : Redis, cache_duration_minutes : int) -> None:
        self.r = redis
        self.prefix = "cache"
        self.expire_time = cache_duration_minutes * 60
    
    async def get(self, input: str) -> str | None:
        return await self.r.get(f"{self.prefix}:{input}")
    
    async def store(self, input: str, output: str) -> None:
        await self.r.setex(f"{self.prefix}:{input}", self.expire_time, output)