"""Test configuration and fixtures for integration tests.

This module provides configuration and fixtures for running integration tests
with real API data. It ensures proper environment setup, logging configuration,
and test data management.
"""

import os
import pytest
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

from smeanalytica.utils.logger import setup_logger
from smeanalytica.config.test_config import TestConfig
from smeanalytica.shared.data_cache import DataCache

# Initialize logger
logger = setup_logger(__name__, logging.INFO)

def pytest_configure(config):
    """Configure test environment with proper security and logging."""
    try:
        # Load test environment variables
        env_file = Path(__file__).parent / ".env.test"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Validate required environment variables
        required_vars = ["GOOGLE_PLACES_API_KEY", "RAPIDAPI_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Set up test directories with proper permissions
        test_data_dir = Path(__file__).parent / "test_data"
        test_data_dir.mkdir(mode=0o755, exist_ok=True)
        
        # Initialize test cache
        cache_dir = test_data_dir / "cache"
        cache_dir.mkdir(mode=0o755, exist_ok=True)
        DataCache.initialize(str(cache_dir))
        
        logger.info("Test environment configured successfully")
        
    except Exception as e:
        logger.error(f"Failed to configure test environment: {str(e)}")
        raise

@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration with secure defaults."""
    return TestConfig(
        test_data_dir=str(Path(__file__).parent / "test_data"),
        cache_duration=3600,  # 1 hour in seconds
        max_retries=3,
        timeout=30,
        batch_size=5,
        rate_limit={
            "requests_per_second": 2,
            "burst_size": 5
        },
        security={
            "max_api_key_age": 86400,  # 24 hours in seconds
            "require_https": True,
            "validate_ssl": True
        }
    )

@pytest.fixture(scope="session")
def test_businesses() -> Dict[str, Any]:
    """Provide test business data with proper validation."""
    return {
        "valid_business": {
            "name": "La Pepica",
            "location": "Valencia, Spain",
            "expected_fields": [
                "name", "rating", "review_count", "price_level",
                "categories", "photos", "reviews"
            ],
            "validation_rules": {
                "rating": lambda x: 0 <= x <= 5,
                "review_count": lambda x: x >= 0,
                "price_level": lambda x: x in ["$", "$$", "$$$", "$$$$"]
            }
        },
        "invalid_business": {
            "name": "NonexistentBusiness12345",
            "location": "InvalidLocation",
            "expected_error": "Business not found",
            "error_code": "NOT_FOUND"
        }
    }

@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up test cache before and after each test."""
    cache = DataCache()
    cache.clear()
    yield
    cache.clear()
    logger.info("Test cache cleaned up")
