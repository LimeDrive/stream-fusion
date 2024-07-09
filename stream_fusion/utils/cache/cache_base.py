import hashlib
from abc import ABC, abstractmethod
from typing import Any, Callable

from stream_fusion.logging_config import logger

class CacheBase(ABC):
    def __init__(self, config: dict):
        """
        Initialize the cache base class.
        Args:
            config (dict): Configuration dictionary for the cache.
        """
        self.logger = logger
        self.config = config

    @abstractmethod
    def can_cache(self) -> bool:
        """
        Check if caching is possible.
        Returns:
            bool: True if caching is possible, False otherwise.
        """
        pass

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache.
        Args:
            key (str): The cache key.
        Returns:
            Any: The cached value if found, None otherwise.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.
        Args:
            key (str): The cache key.
            value (Any): The value to be cached.
        """
        pass

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator for caching function results.
        Args:
            func (Callable): The function to be cached.
        Returns:
            Callable: The wrapped function with caching functionality.
        """
        def wrapper(*args, **kwargs):
            if not self.can_cache():
                self.logger.error("Cache is not available or cannot be used.")
                return func(*args, **kwargs)

            key = self.generate_key(func.__name__, *args, **kwargs)
            cached_result = self.get(key)

            if cached_result is not None:
                self.logger.info(f"Result found in cache for key: {key}")
                return cached_result

            result = func(*args, **kwargs)
            self.set(key, result)
            return result

        return wrapper

    def generate_key(self, func_name: str, *args, **kwargs) -> str:
        """
        Generate a cache key based on function name and arguments.
        Args:
            func_name (str): Name of the function being cached.
            *args: Positional arguments of the function.
            **kwargs: Keyword arguments of the function.
        Returns:
            str: A hashed key string.
        """
        arg_string = f"{func_name}:{str(args)}:{str(kwargs)}"
        hashed_key = hashlib.sha256(arg_string.encode("utf-8")).hexdigest()
        return hashed_key[:16]