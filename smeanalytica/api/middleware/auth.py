"""Authentication middleware for the FastAPI application."""

import os
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...core.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle authentication in the request-response cycle."""
        try:
            # Skip auth for health check endpoints
            if request.url.path.startswith("/health"):
                return await call_next(request)
                
            # Get API key from header
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                raise AuthenticationError("API key is required")
                
            # Validate API key (replace with your actual validation logic)
            valid_api_key = os.getenv("API_KEY")
            if not valid_api_key or api_key != valid_api_key:
                raise AuthenticationError("Invalid API key")
                
            # Add user info to request state
            request.state.user = {
                "api_key": api_key,
                # Add other user info as needed
            }
            
            return await call_next(request)
            
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "authentication_error",
                    "message": str(e)
                }
            )
            
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "auth_error",
                    "message": "Authentication process failed"
                }
            )

def require_api_key(func: Callable) -> Callable:
    """Decorator to require API key for specific routes."""
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
                    
        if not request:
            raise AuthenticationError("Could not validate request")
            
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise AuthenticationError("API key is required")
            
        # Validate API key (replace with your actual validation logic)
        valid_api_key = os.getenv("API_KEY")
        if not valid_api_key or api_key != valid_api_key:
            raise AuthenticationError("Invalid API key")
            
        return await func(*args, **kwargs)
        
    return wrapper
