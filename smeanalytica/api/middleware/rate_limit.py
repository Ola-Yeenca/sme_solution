"""Rate limiting middleware for the SME Analytica API."""

from functools import wraps
import time
import logging
from typing import Dict, Callable
from cachetools import TTLCache
from flask import request, jsonify

logger = logging.getLogger(__name__)

# Rate limit configurations
RATE_LIMITS = {
    'analysis': {'requests': 100, 'window': 3600},  # 100 requests per hour
    'search': {'requests': 50, 'window': 3600},     # 50 searches per hour
    'details': {'requests': 200, 'window': 3600}    # 200 detail requests per hour
}

# Cache for storing rate limit data
rate_limit_cache = TTLCache(maxsize=1000, ttl=3600)

class RateLimiter:
    """Rate limiter implementation using sliding window."""
    
    def __init__(self, limit: int, window: int):
        """Initialize rate limiter."""
        self.limit = limit
        self.window = window
        self.requests = []
        
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        
        # Clean old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.window]
        
        # Check if under limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
            
        return False
        
    def get_reset_time(self) -> int:
        """Get time until rate limit resets."""
        if not self.requests:
            return 0
        return int(self.requests[0] + self.window - time.time())
        
def get_rate_limiter(endpoint_type: str) -> RateLimiter:
    """Get or create rate limiter for endpoint type."""
    if endpoint_type not in rate_limit_cache:
        config = RATE_LIMITS.get(endpoint_type, {'requests': 50, 'window': 3600})
        rate_limit_cache[endpoint_type] = RateLimiter(
            config['requests'],
            config['window']
        )
    return rate_limit_cache[endpoint_type]

def rate_limit(endpoint_type: str) -> Callable:
    """Decorator to apply rate limiting to endpoints."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client identifier (API key or IP)
            client_id = request.headers.get('X-API-Key') or request.remote_addr
            cache_key = f"{endpoint_type}:{client_id}"
            
            limiter = get_rate_limiter(endpoint_type)
            
            if not limiter.is_allowed(cache_key):
                reset_time = limiter.get_reset_time()
                logger.warning(f"Rate limit exceeded for {cache_key}")
                return jsonify({
                    'status': 'error',
                    'error': 'Rate Limit Exceeded',
                    'message': 'Too many requests',
                    'reset_in': reset_time
                }), 429
                
            # Add rate limit headers
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response, status_code = response
            else:
                status_code = 200
                
            headers = {
                'X-RateLimit-Limit': str(limiter.limit),
                'X-RateLimit-Remaining': str(limiter.limit - len(limiter.requests)),
                'X-RateLimit-Reset': str(limiter.get_reset_time())
            }
            
            if isinstance(response, dict):
                return jsonify(response), status_code, headers
            return response, status_code, headers
            
        return decorated
    return decorator
