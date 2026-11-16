import json
from collections import defaultdict
from redis.asyncio import Redis
from app.core.config import settings

class FeatureStore:
    def __init__(self):
        self.redis = None
        self.local = defaultdict(dict)

    async def connect(self):
        try:
            client = Redis.from_url(settings.redis_url, decode_responses=True,
                                    socket_connect_timeout=0.15, socket_timeout=0.15)
            await client.ping()
            self.redis = client
        except Exception:
            self.redis = None

    async def close(self):
        if self.redis:
            await self.redis.aclose()

    async def get(self, key: str, default=None):
        try:
            if self.redis:
                value = await self.redis.get(key)
                return json.loads(value) if value else default
        except Exception:
            pass
        return self.local.get(key, default)

    async def set(self, key: str, value):
        self.local[key] = value
        try:
            if self.redis:
                await self.redis.set(key, json.dumps(value), ex=86400)
        except Exception:
            pass

    async def increment(self, key: str, field: str, amount: int = 1):
        current = await self.get(key, {})
        current[field] = int(current.get(field, 0)) + amount
        await self.set(key, current)
        return current
