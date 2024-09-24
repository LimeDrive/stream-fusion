from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends, Request
from redis import Redis
from stream_fusion.settings import settings
from stream_fusion.utils.cache.local_redis import RedisCache

# Redis config
@lru_cache()
def get_redis_config():
    return {
        "redisHost": settings.redis_host,
        "redisPort": settings.redis_port,
        "redisDb": settings.redis_db,
        "redisExpiration": settings.redis_expiration,
    }

# Redis cache
def create_redis_cache():
    return RedisCache(get_redis_config())

# Redis cache dependency
def get_redis_cache():
    return create_redis_cache()

# Async generator for Redis cache dependency
async def get_redis_cache_dependency():
    redis_cache = get_redis_cache()
    try:
        yield redis_cache
    finally:
        await redis_cache.close()

# Redis connection pool
def get_redis(request: Request) -> Redis:
    return Redis(connection_pool=request.app.state.redis_pool)

# Async generator for Redis connection pool
async def get_redis_client(request: Request) -> AsyncGenerator[Redis, None]:
    redis_client = Redis(connection_pool=request.app.state.redis_pool)
    try:
        yield redis_client
    finally:
        redis_client.close()

# Dependency for Redis connection pool
def get_redis_dependency():
    return Depends(get_redis_client)
