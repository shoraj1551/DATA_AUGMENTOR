import hashlib
import json
import time
from typing import Any, Optional, Callable
from functools import wraps


class LLMCache:
    """
    In-memory cache for LLM responses with TTL (time-to-live) support.
    """
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 100):
        """
        Initialize the cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries (default: 1 hour)
            max_size: Maximum number of entries to store
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        
        Returns:
            SHA256 hash of the serialized arguments
        """
        # Create a stable representation of the arguments
        key_data = {
            'args': str(args),
            'kwargs': json.dumps(kwargs, sort_keys=True, default=str)
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _is_expired(self, entry: dict) -> bool:
        """Check if a cache entry has expired."""
        return time.time() - entry['timestamp'] > self.ttl_seconds
    
    def _evict_oldest(self):
        """Remove the oldest entry from the cache."""
        if not self._cache:
            return
        
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k]['timestamp'])
        del self._cache[oldest_key]
        self._stats['evictions'] += 1
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if self._is_expired(entry):
            del self._cache[key]
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        return entry['value']
    
    def set(self, key: str, value: Any):
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Evict oldest if at max capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_oldest()
        
        self._cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with hits, misses, evictions, and hit rate
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'evictions': self._stats['evictions'],
            'hit_rate': f"{hit_rate:.2f}%",
            'total_entries': len(self._cache)
        }
    
    def cached(self, func: Callable) -> Callable:
        """
        Decorator to cache function results.
        
        Usage:
            @cache.cached
            def my_function(arg1, arg2):
                return expensive_operation(arg1, arg2)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = self._generate_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = self.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.set(cache_key, result)
            
            return result
        
        return wrapper


# Global cache instance
llm_cache = LLMCache(ttl_seconds=3600, max_size=100)
