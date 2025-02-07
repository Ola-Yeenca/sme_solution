"""Caching module for business data."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

logger = logging.getLogger(__name__)

class DataCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
        self._lock = asyncio.Lock()
        self.initialized = False
        self.cleanup_task = None
    
    async def initialize(self):
        """Initialize cache and start cleanup task."""
        if self.initialized:
            return self
            
        # Start periodic cleanup task
        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
        self.initialized = True
        logger.info("Cache initialized successfully")
        return self
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache if not expired."""
        if not self.initialized:
            raise RuntimeError("Cache not initialized. Call initialize() first.")
        
        async with self._lock:
            try:
                if key not in self._cache:
                    self._misses += 1
                    logger.info(f"Cache miss for key: {key}")
                    return None
                
                cached = self._cache[key]
                if self._is_expired(cached['timestamp']):
                    self._misses += 1
                    del self._cache[key]
                    logger.info(f"Cache expired for key: {key}")
                    return None
                
                self._hits += 1
                logger.info(f"Cache hit for key: {key}")
                return cached['data']
                
            except Exception as e:
                logger.error(f"Error retrieving from cache: {str(e)}")
                return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: int = None) -> None:
        """Set value in cache with current timestamp."""
        if not self.initialized:
            raise RuntimeError("Cache not initialized. Call initialize() first.")
        
        async with self._lock:
            try:
                if ttl is None:
                    ttl = self._ttl_seconds
                self._cache[key] = {
                    'data': value,
                    'timestamp': datetime.now() + timedelta(seconds=ttl)
                }
            except Exception as e:
                logger.error(f"Error setting cache value: {str(e)}")
    
    async def invalidate(self, key: str) -> None:
        """Remove item from cache."""
        if not self.initialized:
            raise RuntimeError("Cache not initialized. Call initialize() first.")
        
        async with self._lock:
            try:
                if key in self._cache:
                    del self._cache[key]
            except Exception as e:
                logger.error(f"Error invalidating cache key: {str(e)}")
    
    async def clear(self) -> None:
        """Clear all items from cache."""
        if not self.initialized:
            raise RuntimeError("Cache not initialized. Call initialize() first.")
        
        async with self._lock:
            try:
                self._cache.clear()
                self._hits = 0
                self._misses = 0
            except Exception as e:
                logger.error(f"Error clearing cache: {str(e)}")
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cached item has expired."""
        age = datetime.now() - timestamp
        return age.total_seconds() > 0
    
    async def _periodic_cleanup(self):
        """Periodically remove expired entries."""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = [
                    key for key, cached in self._cache.items()
                    if (current_time - cached['timestamp']).total_seconds() > 0
                ]
                
                for key in expired_keys:
                    await self.invalidate(key)
                
                # Sleep for 1/10th of TTL
                await asyncio.sleep(self._ttl_seconds / 10)
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {str(e)}")
                await asyncio.sleep(60)  # Sleep for a minute on error
    
    async def shutdown(self):
        """Shutdown cache and cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        await self.clear()
        self.initialized = False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            return {
                'size': len(self._cache),
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': self.hit_rate,
                'ttl_seconds': self._ttl_seconds
            }
