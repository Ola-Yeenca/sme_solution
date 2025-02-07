"""Error handler middleware for the FastAPI application."""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...core.exceptions import (
    BusinessAnalysisError,
    ValidationError,
    AnalysisError,
    DataFetchError,
    ModelError,
    ConfigurationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    APIError
)

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors in the application."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors in the request-response cycle."""
        try:
            return await call_next(request)
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "validation_error",
                    "message": str(e),
                    "details": e.details if hasattr(e, 'details') else None
                }
            )
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "authentication_error",
                    "message": str(e)
                }
            )
            
        except AuthorizationError as e:
            logger.warning(f"Authorization error: {str(e)}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "authorization_error",
                    "message": str(e)
                }
            )
            
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {str(e)}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": str(e)
                }
            )
            
        except (AnalysisError, DataFetchError, ModelError) as e:
            logger.error(f"Business operation error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "operation_error",
                    "message": str(e),
                    "details": e.details if hasattr(e, 'details') else None
                }
            )
            
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            return JSONResponse(
                status_code=e.status_code or 500,
                content={
                    "error": "api_error",
                    "message": str(e),
                    "details": e.response if hasattr(e, 'response') else None
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "reference": request.state.request_id if hasattr(request.state, 'request_id') else None
                }
            ) 