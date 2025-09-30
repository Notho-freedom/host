"""Caching utilities with TTL support."""

import time
import asyncio
import hashlib
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL."""
    value: Any
    expires_at: float
    hits: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > self.expires_at


class TTLCache:
    """Thread-safe TTL cache implementation."""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def _generate_key(self, key: str) -> str:
        """Generate normalized cache key."""
        return hashlib.md5(str(key).encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            cache_key = self._generate_key(key)
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired:
                del self._cache[cache_key]
                self._stats['misses'] += 1
                return None
            
            entry.hits += 1
            self._stats['hits'] += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        async with self._lock:
            cache_key = self._generate_key(key)
            expires_at = time.time() + (ttl or self.default_ttl)
            
            # Evict expired entries if cache is full
            if len(self._cache) >= self.max_size:
                await self._evict_expired()
                
                # If still full, evict least used
                if len(self._cache) >= self.max_size:
                    await self._evict_lru()
            
            self._cache[cache_key] = CacheEntry(value, expires_at)
            self._stats['sets'] += 1
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            cache_key = self._generate_key(key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._stats['evictions'] += len(self._cache)
    
    async def _evict_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.expires_at <= current_time
        ]
        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1
    
    async def _evict_lru(self) -> None:
        """Remove least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].hits)
        del self._cache[lru_key]
        self._stats['evictions'] += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': round(hit_rate, 3),
                'stats': self._stats.copy()
            }


class CacheManager:
    """Manage multiple caches with different TTLs."""
    
    def __init__(self):
        self.caches: Dict[str, TTLCache] = {}
    
    def get_cache(self, name: str, ttl: int = 300, max_size: int = 1000) -> TTLCache:
        """Get or create a named cache."""
        if name not in self.caches:
            self.caches[name] = TTLCache(default_ttl=ttl, max_size=max_size)
        return self.caches[name]
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        stats = {}
        for name, cache in self.caches.items():
            stats[name] = await cache.get_stats()
        return stats


def cache_async(ttl: int = 300, cache_name: str = "default"):
    """Decorator for caching async function results."""
    
    def decorator(func: Callable):
        cache = cache_manager.get_cache(cache_name, ttl=ttl)
        
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            result = await cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Compute and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl=ttl)
            return result
        
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = CacheManager()