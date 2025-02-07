"""Decorators for the SME Analytica application."""

import os
import functools
import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional
from flask import request, jsonify

from .exceptions import AuthenticationError, RateLimitError, CacheError

logger = logging.getLogger(__name__)

# Simple in-memory cache for rate limiting and caching
_rate_limit_store: Dict[str, Dict[str, Any]] = {}
_cache_store: Dict[str, Dict[str, Any]] = {}

def require_api_key(func: Callable) -> Callable:
    """Decorator to require API key authentication."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'status': 'error',
                'error': 'Authentication error',
                'message': 'API key is required'
            }), 401
            
        # Get expected API key from environment or use development key
        expected_key = os.getenv('API_KEY', 'smeanalytica-dev-12345')
        
        # Validate API key
        if api_key != expected_key:
            logger.warning(f"Invalid API key used: {api_key}")
            return jsonify({
                'status': 'error',
                'error': 'Authentication error',
                'message': 'Invalid API key'
            }), 401
            
        return func(*args, **kwargs)
    return wrapper

def rate_limit(max_requests: int = 100, window_seconds: int = 3600) -> Callable:
    """Decorator to implement rate limiting."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get client identifier (IP address or API key)
            client_id = request.headers.get('X-API-Key', request.remote_addr)
            
            # Get current timestamp
            now = datetime.now()
            
            # Initialize or get client's rate limit data
            if client_id not in _rate_limit_store:
                _rate_limit_store[client_id] = {
                    'requests': 0,
                    'window_start': now
                }
            
            # Reset window if expired
            client_data = _rate_limit_store[client_id]
            window_start = client_data['window_start']
            if now - window_start > timedelta(seconds=window_seconds):
                client_data['requests'] = 0
                client_data['window_start'] = now
            
            # Check rate limit
            if client_data['requests'] >= max_requests:
                return jsonify({
                    'status': 'error',
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window_seconds} seconds'
                }), 429
            
            # Increment request count
            client_data['requests'] += 1
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cache(ttl: int = 300):  # Default TTL of 5 minutes
    """Cache decorator that respects force_refresh and cache control headers."""
    def decorator(func: Callable) -> Callable:
        cache_data = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if force refresh is requested
            json_data = request.get_json(silent=True) or {}
            force_refresh = json_data.get('force_refresh', False)
            
            # Check cache control headers
            if 'Cache-Control' in request.headers:
                cache_control = request.headers['Cache-Control'].lower()
                if 'no-cache' in cache_control or 'no-store' in cache_control:
                    force_refresh = True
            
            current_time = time.time()
            
            # Get cached data if it exists and is not expired
            cached_item = cache_data.get(cache_key)
            
            if not force_refresh and cached_item:
                data, timestamp = cached_item
                if current_time - timestamp < ttl:
                    return data
            
            # Get fresh data
            result = func(*args, **kwargs)
            
            # Cache the new result
            cache_data[cache_key] = (result, current_time)
            
            return result
            
        def clear_cache():
            """Clear all cached data."""
            cache_data.clear()
            
        wrapper.clear_cache = clear_cache
        return wrapper
    return decorator
