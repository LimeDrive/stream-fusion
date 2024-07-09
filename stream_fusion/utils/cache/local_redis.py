import asyncio
import inspect
import jsonpickle
import time
from typing import Any, List
import hashlib
import redis
from stream_fusion.settings import settings
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.utils.cache.cache_base import CacheBase

class RedisCache(CacheBase):
    def __init__(self, config):
        super().__init__(config)
        self.redis_host = settings.redis_host
        self.redis_port = settings.redis_port
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}"
        self._redis_client = None
        self.media_expiration = settings.redis_expiration

    def get_redis_client(self):
        if not self._redis_client:
            try:
                self._redis_client = redis.Redis.from_url(
                    self.redis_url,
                    max_connections=10
                )
            except redis.ConnectionError:
                self.logger.error("Failed to create Redis client")
                self._redis_client = None
        return self._redis_client

    def get_list(self, key: str) -> List[Any]:
        result = self.get(key)
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

    def clear(self) -> None:
        try:
            client = self.get_redis_client()
            client.flushdb()
            self.logger.info("Cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

    def get_or_set(self, func: callable, *args, **kwargs) -> Any:
        self.logger.debug(f"Entering get_or_set for function: {func.__name__}")
        start_time = time.time()

        if not self.can_cache():
            self.logger.debug("Cache is not available, executing function directly")
            return self._execute_func(func, *args, **kwargs)

        key = self.generate_key(func.__name__, *args, **kwargs)
        self.logger.debug(f"Generated cache key: {key}")

        cached_result = self.get(key)
        self.logger.debug(f"Attempted to get result from cache. Found: {cached_result is not None}")

        if cached_result is not None:
            self.logger.debug(f"Returning cached result for key: {key}")
            return cached_result

        self.logger.debug(f"Cache miss for key: {key}. Executing function.")
        result = self._execute_func(func, *args, **kwargs)
        self.logger.debug(f"Function execution completed. Setting result in cache.")
        self.set(key, result)

        end_time = time.time()
        self.logger.debug(f"get_or_set completed in {end_time - start_time:.2f} seconds")
        return result

    def _execute_func(self, func, *args, **kwargs):
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
            loop = asyncio.get_event_loop()
            try:
                result = loop.run_until_complete(func(**call_args))
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

    def can_cache(self) -> bool:
        self.logger.debug("Checking if caching is possible")
        try:
            client = self.get_redis_client()
            result = client.ping()
            self.logger.debug(f"Redis ping result: {result}")
            return result
        except redis.ConnectionError:
            self.logger.error("Unable to connect to Redis")
            return False

    def get(self, key: str) -> Any:
        self.logger.debug(f"Attempting to get value for key: {key}")
        try:
            client = self.get_redis_client()
            cached_result = client.get(key)
            if cached_result:
                self.logger.debug(f"Value found in cache for key: {key}")
                return jsonpickle.decode(cached_result)
            self.logger.debug(f"No value found in cache for key: {key}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving from Redis: {e}")
            return None

    def set(self, key: str, value: Any, expiration: int = None) -> None:
        self.logger.debug(f"Attempting to set value for key: {key}")
        if expiration is None:
            expiration = self.media_expiration
        
        try:
            client = self.get_redis_client()
            cached_data = jsonpickle.encode(value)
            result = client.set(key, cached_data, ex=expiration)
            self.logger.debug(f"Set operation result for key {key}: {result}")
        except Exception as e:
            self.logger.error(f"Error storing in Redis: {e}")

    def delete(self, key: str) -> bool:
        try:
            client = self.get_redis_client()
            return bool(client.delete(key))
        except Exception as e:
            self.logger.error(f"Error deleting key from Redis: {e}")
            return False

    def exists(self, key: str) -> bool:
        try:
            client = self.get_redis_client()
            return bool(client.exists(key))
        except Exception as e:
            self.logger.error(f"Error checking key existence in Redis: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        try:
            client = self.get_redis_client()
            return client.ttl(key)
        except Exception as e:
            self.logger.error(f"Error getting TTL from Redis: {e}")
            return -1

    def update_expiration(self, key: str, expiration: int) -> bool:
        try:
            client = self.get_redis_client()
            return bool(client.expire(key, expiration))
        except Exception as e:
            self.logger.error(f"Error updating expiration in Redis: {e}")
            return False

    def close(self):
        if self._redis_client:
            self._redis_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
