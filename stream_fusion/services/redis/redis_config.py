from functools import lru_cache
from fastapi import Depends
from stream_fusion.settings import settings
from stream_fusion.utils.cache.local_redis import RedisCache

@lru_cache()
def get_redis_config():
    return {
        "redisHost": settings.redis_host,
        "redisPort": settings.redis_port,
        "redisExpiration": settings.redis_expiration,
    }

@lru_cache()
def create_redis_cache():
    return RedisCache(get_redis_config())

def get_redis_cache():
    return create_redis_cache()

async def get_redis_dependency():
    redis_cache = get_redis_cache()
    try:
        yield redis_cache
    finally:
        redis_cache.close()