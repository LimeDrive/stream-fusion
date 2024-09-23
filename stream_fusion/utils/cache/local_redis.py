import asyncio
import inspect
import jsonpickle
import time
from typing import Any, List
import hashlib
from redis.asyncio import Redis
from stream_fusion.settings import settings
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.utils.cache.cache_base import CacheBase

class RedisCache(CacheBase):
    def __init__(self, config):
        super().__init__(config)
        self.redis_host = settings.redis_host
        self.redis_port = settings.redis_port
        self.redis_db = settings.redis_db
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        self._redis_client = None
        self.media_expiration = settings.redis_expiration

    async def get_redis_client(self):
        if not self._redis_client:
            try:
                self._redis_client = Redis.from_url(
                    self.redis_url,
                    max_connections=10
                )
            except Exception as e:
                self.logger.error(f"Failed to create Redis client: {e}")
                self._redis_client = None
        return self._redis_client
    
    async def reconnect(self):
        self.logger.info("Attempting to reconnect to Redis")
        self._redis_client = None
        return await self.get_redis_client()

    async def execute_with_retry(self, operation, *args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await operation(*args, **kwargs)
            except ConnectionError:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Redis connection lost. Attempting reconnection (attempt {attempt + 1}/{max_retries})")
                    await self.reconnect()
                else:
                    self.logger.error("Max retries reached. Unable to reconnect to Redis.")
                    raise

    async def get_list(self, key: str) -> List[Any]:
        result = await self.get(key)
        if isinstance(result, list):
            return result
        elif result is not None:
            return [result]
        return None

    def generate_key(self, func_name: str, *args, **kwargs) -> str:
        media = kwargs.get('media')
        if media is None and args:
            media = next((arg for arg in args if isinstance(arg, (Movie, Series))), None)
        
        if media:
            if isinstance(media, Movie):
                key_string = f"movie:{media.titles[0]}:{media.languages[0]}"
            elif isinstance(media, Series):
                key_string = f"series:{media.titles[0]}:{media.languages[0]}:{media.season}"
            else:
                raise TypeError("Only Movie and Series are allowed as media!")
        else:
            key_string = f"{func_name}:{str(args)}:{str(kwargs)}"
        
        hashed_key = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
        return hashed_key[:16]

    async def clear(self) -> None:
        try:
            client = await self.get_redis_client()
            await client.flushdb()
            self.logger.info("Cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

    async def get_or_set(self, func: callable, *args, **kwargs) -> Any:
        self.logger.debug(f"Entering get_or_set for function: {func.__name__}")
        start_time = time.time()

        if not await self.can_cache():
            self.logger.debug("Cache is not available, executing function directly")
            return await self._execute_func(func, *args, **kwargs)

        key = self.generate_key(func.__name__, *args, **kwargs)
        self.logger.debug(f"Generated cache key: {key}")

        cached_result = await self.get(key)
        self.logger.debug(f"Attempted to get result from cache. Found: {cached_result is not None}")

        if cached_result is not None:
            self.logger.debug(f"Returning cached result for key: {key}")
            return cached_result

        self.logger.debug(f"Cache miss for key: {key}. Executing function.")
        result = await self._execute_func(func, *args, **kwargs)
        self.logger.debug(f"Function execution completed. Setting result in cache.")
        await self.set(key, result)

        end_time = time.time()
        self.logger.debug(f"get_or_set completed in {end_time - start_time:.2f} seconds")
        return result

    async def _execute_func(self, func, *args, **kwargs):
        self.logger.debug(f"Executing function: {func.__name__}")
        start_time = time.time()

        sig = inspect.signature(func)
        params = sig.parameters

        self.logger.debug(f"Function {func.__name__} expects {len(params)} arguments")
        self.logger.debug(f"Received args: {args}, kwargs: {kwargs}")

        call_args = {}
        for i, (param_name, param) in enumerate(params.items()):
            if i < len(args):
                call_args[param_name] = args[i]
            elif param_name in kwargs:
                call_args[param_name] = kwargs[param_name]
            elif param.default is not param.empty:
                call_args[param_name] = param.default
            else:
                self.logger.error(f"Missing required argument: {param_name}")
                raise TypeError(f"Missing required argument: {param_name}")

        self.logger.debug(f"Prepared arguments for {func.__name__}: {call_args}")

        if asyncio.iscoroutinefunction(func):
            self.logger.debug(f"Function {func.__name__} is asynchronous")
            try:
                result = await func(**call_args)
                self.logger.debug(f"Asynchronous function {func.__name__} completed successfully")
            except Exception as e:
                self.logger.error(f"Error executing asynchronous function {func.__name__}: {str(e)}")
                raise
        else:
            self.logger.debug(f"Function {func.__name__} is synchronous")
            try:
                result = func(**call_args)
                self.logger.debug(f"Synchronous function {func.__name__} completed successfully")
            except Exception as e:
                self.logger.error(f"Error executing synchronous function {func.__name__}: {str(e)}")
                raise

        end_time = time.time()
        self.logger.debug(f"Function {func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result

    async def can_cache(self) -> bool:
        self.logger.debug("Checking if caching is possible")
        try:
            client = await self.get_redis_client()
            result = await client.ping()
            self.logger.debug(f"Redis ping result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Unable to connect to Redis: {e}")
            return False

    async def get(self, key: str) -> Any:
        async def get_operation():
            client = await self.get_redis_client()
            cached_result = await client.get(key)
            if cached_result:
                return jsonpickle.decode(cached_result)
            return None

        return await self.execute_with_retry(get_operation)

    async def set(self, key: str, value: Any, expiration: int = None) -> None:
        if expiration is None:
            expiration = self.media_expiration

        async def set_operation():
            client = await self.get_redis_client()
            cached_data = jsonpickle.encode(value)
            return await client.set(key, cached_data, ex=expiration)

        await self.execute_with_retry(set_operation)

    async def delete(self, key: str) -> bool:
        async def delete_operation():
            client = await self.get_redis_client()
            return bool(await client.delete(key))

        return await self.execute_with_retry(delete_operation)

    async def exists(self, key: str) -> bool:
        async def exists_operation():
            client = await self.get_redis_client()
            return bool(await client.exists(key))

        return await self.execute_with_retry(exists_operation)

    async def get_ttl(self, key: str) -> int:
        async def get_ttl_operation():
            client = await self.get_redis_client()
            return await client.ttl(key)

        return await self.execute_with_retry(get_ttl_operation)
    
    async def update_expiration(self, key: str, expiration: int) -> bool:
        async def update_expiration_operation():
            client = await self.get_redis_client()
            return bool(await client.expire(key, expiration))

        return await self.execute_with_retry(update_expiration_operation)

    async def close(self):
        if self._redis_client:
            await self._redis_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()