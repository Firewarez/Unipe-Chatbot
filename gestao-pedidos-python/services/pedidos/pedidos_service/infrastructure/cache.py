from typing import Protocol

from redis.asyncio import Redis


class Cache(Protocol):
    async def get(self, key: str) -> str | None:
        ...

    async def set(self, key: str, value: str) -> None:
        ...

    async def delete(self, key: str) -> None:
        ...


class NullCache:
    async def get(self, key: str) -> str | None:
        return None

    async def set(self, key: str, value: str) -> None:
        return None

    async def delete(self, key: str) -> None:
        return None


class RedisCache:
    def __init__(self, redis_url: str, ttl_seconds: int = 60) -> None:
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.ttl_seconds = ttl_seconds

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str) -> None:
        await self.redis.set(key, value, ex=self.ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

