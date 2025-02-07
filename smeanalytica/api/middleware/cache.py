"""Cache middleware for the SME Analytica API."""

from functools import wraps
import hashlib
import json
import logging
import time
from typing import Dict, Any, Callable, Optional
from cachetools import TTLCache
from flask import request, Response, jsonify

logger = logging.getLogger(__name__)

# Cache configurations
CACHE_CONFIGS = {
    'analysis': {'maxsize': 1000, 'ttl': 3600},     # 1 hour for analysis results
    'search': {'maxsize': 500, 'ttl': 1800},        # 30 minutes for search results
    'details': {'maxsize': 2000, 'ttl': 7200}       # 2 hours for business details
}

# Cache storage
caches: Dict[str, TTLCache] = {}

def get_cache(cache_type: str) -> TTLCache:
    """Get or create cache for the specified type."""
    if cache_type not in caches:
        config = CACHE_CONFIGS.get(cache_type, {'maxsize': 100, 'ttl': 3600})
        caches[cache_type] = TTLCache(
            maxsize=config['maxsize'],
            ttl=config['ttl']
        )
    return caches[cache_type]

def generate_cache_key(data: Dict[str, Any]) -> str:
    """Generate a unique cache key from request data."""
    # Sort dictionary to ensure consistent key generation
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()

def should_skip_cache(request_obj: Any) -> bool:
    """Determine if caching should be skipped."""
    # Skip cache for non-GET requests
    if request_obj.method != 'GET':
        return True
        
    # Skip cache if explicitly requested
    if request_obj.headers.get('Cache-Control') == 'no-cache':
        return True
        
    return False

def cache(cache_type: str = 'default', ttl: Optional[int] = None) -> Callable:
    """Decorator to cache API responses."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if should_skip_cache(request):
                return f(*args, **kwargs)
                
            # Generate cache key from request data
            cache_data = {
                'path': request.path,
                'args': dict(request.args),
                'json': request.get_json(silent=True),
                'headers': {
                    k: v for k, v in request.headers.items()
                    if k in ['X-API-Key', 'Accept-Language']
                }
            }
            cache_key = generate_cache_key(cache_data)
            
            # Try to get from cache
            cache_storage = get_cache(cache_type)
            cached_response = cache_storage.get(cache_key)
            
            if cached_response:
                response_data, status_code, headers = cached_response
                logger.debug(f"Cache hit for {cache_key}")
                return jsonify(response_data), status_code, headers
                
            # Get fresh response
            response = f(*args, **kwargs)
            
            # Parse response
            if isinstance(response, tuple):
                response_data, status_code = response
                headers = {}
            else:
                response_data = response
                status_code = 200
                headers = {}
                
            # Only cache successful responses
            if 200 <= status_code < 300:
                cache_storage[cache_key] = (response_data, status_code, headers)
                logger.debug(f"Cached response for {cache_key}")
                
            # Add cache headers
            headers.update({
                'X-Cache': 'MISS',
                'X-Cache-TTL': str(ttl or CACHE_CONFIGS[cache_type]['ttl'])
            })
            
            return jsonify(response_data), status_code, headers
            
        return decorated
    return decorator

def invalidate_cache(cache_type: str, pattern: Optional[str] = None):
    """Invalidate cache entries matching the pattern."""
    if cache_type in caches:
        if pattern:
            # Remove specific entries matching pattern
            keys_to_remove = [
                key for key in caches[cache_type].keys()
                if pattern in str(key)
            ]
            for key in keys_to_remove:
                del caches[cache_type][key]
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching {pattern}")
        else:
            # Clear entire cache
            caches[cache_type].clear()
            logger.info(f"Cleared entire {cache_type} cache")
