# ============================================================
# cache.py — Connects to Redis for caching
# Cache = store frequent results temporarily so we skip the DB
# Example: machine status is cached for 10 seconds
# ============================================================

import redis.asyncio as aioredis   # async Redis client
from app.config import settings
from app.logger import log

# Global Redis connection
redis_client = None

async def connect_cache():
    """Called on app startup — opens Redis connection."""
    global redis_client
    log.info("Connecting to Redis...")
    redis_client = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True          # Return strings, not bytes
    )
    log.info("Redis connected.")

async def close_cache():
    """Called on app shutdown — closes Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        log.info("Redis connection closed.")

def get_cache():
    """Returns the Redis client. Use this in routes to read/write cache."""
    return redis_client

# How caching works in a route:
#
# cache = get_cache()
#
# # Try cache first (fast)
# cached = await cache.get(f"machine:{id}:status")
# if cached:
#     return cached                          # Return instantly from cache
#
# # Cache miss — go to MongoDB (slow)
# result = await db["machines"].find_one({"_id": id})
#
# # Save to cache for 10 seconds so next request is fast
# await cache.setex(f"machine:{id}:status", 10, result)
# return result
