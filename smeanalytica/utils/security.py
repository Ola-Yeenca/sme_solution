"""Security utilities for SME Analytica.

This module provides security-related functions for validating API responses,
sanitizing data, and ensuring secure data handling throughout the application.
"""

import logging
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def validate_api_response(
    response: Dict[str, Any],
    security_config: Dict[str, Any]
) -> bool:
    """Validate API response for security concerns.
    
    Args:
        response: API response data to validate
        security_config: Security configuration settings
        
    Returns:
        True if validation passes, False otherwise
        
    Raises:
        ValueError: If response contains potentially malicious content
    """
    try:
        # Check for common security issues
        if not _check_data_sanitization(response):
            raise ValueError("Response contains potentially unsafe data")
        
        # Validate SSL/TLS if required
        if security_config.get("require_https", True):
            if not _validate_https(response):
                raise ValueError("HTTPS validation failed")
        
        # Check response size
        if not _check_response_size(response):
            raise ValueError("Response size exceeds safe limits")
        
        # Validate data types and structure
        if not _validate_data_types(response):
            raise ValueError("Invalid data types in response")
        
        return True
        
    except Exception as e:
        logger.error(f"API response validation failed: {str(e)}")
        return False

def _check_data_sanitization(data: Dict[str, Any]) -> bool:
    """Check if data is properly sanitized.
    
    Args:
        data: Data to check for sanitization
        
    Returns:
        True if data is properly sanitized, False otherwise
    """
    if isinstance(data, dict):
        return all(_check_data_sanitization(v) for v in data.values())
    elif isinstance(data, list):
        return all(_check_data_sanitization(item) for item in data)
    elif isinstance(data, str):
        # Check for common injection patterns
        dangerous_patterns = [
            "javascript:",
            "data:",
            "<script",
            "onclick=",
            "onerror=",
            "eval(",
            "document.cookie"
        ]
        return not any(pattern in data.lower() for pattern in dangerous_patterns)
    return True

def _validate_https(response: Dict[str, Any]) -> bool:
    """Validate HTTPS-related security aspects of the response.
    
    Args:
        response: Response data to validate
        
    Returns:
        True if HTTPS validation passes, False otherwise
    """
    # Check if URLs in the response use HTTPS
    urls = _extract_urls(response)
    return all(url.startswith("https://") for url in urls)

def _check_response_size(
    response: Dict[str, Any],
    max_size_mb: float = 10.0
) -> bool:
    """Check if response size is within safe limits.
    
    Args:
        response: Response data to check
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        True if size is within limits, False otherwise
    """
    try:
        size_bytes = len(json.dumps(response).encode('utf-8'))
        size_mb = size_bytes / (1024 * 1024)
        return size_mb <= max_size_mb
    except Exception:
        return False

def _validate_data_types(data: Any) -> bool:
    """Validate data types for security concerns.
    
    Args:
        data: Data to validate
        
    Returns:
        True if data types are valid, False otherwise
    """
    if isinstance(data, dict):
        return all(_validate_data_types(v) for v in data.values())
    elif isinstance(data, list):
        return all(_validate_data_types(item) for item in data)
    elif isinstance(data, (str, int, float, bool, type(None))):
        return True
    return False

def _extract_urls(data: Any) -> set:
    """Extract URLs from response data.
    
    Args:
        data: Data to extract URLs from
        
    Returns:
        Set of URLs found in the data
    """
    urls = set()
    
    if isinstance(data, dict):
        for value in data.values():
            urls.update(_extract_urls(value))
    elif isinstance(data, list):
        for item in data:
            urls.update(_extract_urls(item))
    elif isinstance(data, str):
        if data.startswith(("http://", "https://")):
            urls.add(data)
    
    return urls

def hash_api_key(api_key: str) -> str:
    """Create a secure hash of an API key.
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()

def validate_api_key_age(
    api_key_created: datetime,
    max_age_days: int = 90
) -> bool:
    """Validate API key age.
    
    Args:
        api_key_created: Datetime when API key was created
        max_age_days: Maximum allowed age in days
        
    Returns:
        True if API key is within age limit, False otherwise
    """
    max_age = timedelta(days=max_age_days)
    return datetime.now() - api_key_created <= max_age
