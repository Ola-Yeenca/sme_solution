"""Integration tests for data source integrations."""

import os
import pytest
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from smeanalytica.core.data.data_source_manager import DataSourceManager, DataSourceError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_BUSINESS = "Test Restaurant"
TEST_LOCATION = "Valencia, Spain"

@pytest.fixture
def data_manager():
    """Create a DataSourceManager instance for testing."""
    # Set up test environment variables
    os.environ["GOOGLE_PLACES_API_KEY"] = "test_google_key"
    os.environ["YELP_API_KEY"] = "test_yelp_key"
    
    return DataSourceManager()

@pytest.mark.asyncio
async def test_google_places_integration(data_manager):
    """Test Google Places API integration."""
    logger.info("Testing Google Places API integration...")
    
    try:
        # Test business search
        business_data = await data_manager.get_business_data(TEST_BUSINESS)
        assert business_data is not None
        assert "name" in business_data
        assert "rating" in business_data
        
        # Test review fetching
        reviews = await data_manager.get_reviews(TEST_BUSINESS)
        assert isinstance(reviews, list)
        assert all("text" in review for review in reviews)
        
        logger.info("Google Places API test passed ✓")
        
    except Exception as e:
        logger.error("Google Places API test failed: %s", str(e))
        if isinstance(e, DataSourceError):
            # Test fallback to Yelp
            assert data_manager._get_from_yelp.called
        raise

@pytest.mark.asyncio
async def test_yelp_integration(data_manager):
    """Test Yelp API integration."""
    logger.info("Testing Yelp API integration...")
    
    try:
        # Simulate Google Places API failure
        data_manager._get_from_google_places = MagicMock(side_effect=Exception("API Error"))
        
        # Test business search with fallback
        business_data = await data_manager.get_business_data(TEST_BUSINESS)
        assert business_data is not None
        assert "name" in business_data
        assert "rating" in business_data
        
        # Test review fetching with fallback
        reviews = await data_manager.get_reviews(TEST_BUSINESS)
        assert isinstance(reviews, list)
        assert all("text" in review for review in reviews)
        
        logger.info("Yelp API fallback test passed ✓")
        
    except Exception as e:
        logger.error("Yelp API test failed: %s", str(e))
        raise

@pytest.mark.asyncio
async def test_caching_mechanism(data_manager):
    """Test data source caching."""
    logger.info("Testing caching mechanism...")
    
    # First request should hit the API
    start_time = datetime.now()
    data1 = await data_manager.get_business_data(TEST_BUSINESS)
    first_request_time = (datetime.now() - start_time).total_seconds()
    
    # Second request should hit the cache
    start_time = datetime.now()
    data2 = await data_manager.get_business_data(TEST_BUSINESS)
    cached_request_time = (datetime.now() - start_time).total_seconds()
    
    # Verify cache is working
    assert cached_request_time < first_request_time
    assert data1 == data2
    
    logger.info("Cache test passed ✓")
    logger.info("First request: %.2fs, Cached: %.2fs", first_request_time, cached_request_time)

@pytest.mark.asyncio
async def test_rate_limiting(data_manager):
    """Test API rate limiting handling."""
    logger.info("Testing rate limiting...")
    
    # Simulate multiple concurrent requests
    requests = []
    for _ in range(10):
        requests.append(data_manager.get_business_data(TEST_BUSINESS))
    
    # All requests should complete without errors
    results = await asyncio.gather(*requests, return_exceptions=True)
    successful = [r for r in results if not isinstance(r, Exception)]
    
    assert len(successful) > 0, "All requests failed"
    logger.info("Rate limiting test passed ✓")
    logger.info("Successful requests: %d/%d", len(successful), len(results))

@pytest.mark.asyncio
async def test_error_recovery(data_manager):
    """Test error recovery and retry mechanism."""
    logger.info("Testing error recovery...")
    
    # Simulate temporary API failure
    fail_count = 0
    async def mock_api_call(*args, **kwargs):
        nonlocal fail_count
        if fail_count < 2:
            fail_count += 1
            raise Exception("Temporary API Error")
        return {"name": TEST_BUSINESS, "rating": 4.5}
    
    with patch.object(data_manager, '_get_from_google_places', side_effect=mock_api_call):
        # Should succeed after retries
        result = await data_manager.get_business_data(TEST_BUSINESS)
        assert result is not None
        assert result["name"] == TEST_BUSINESS
    
    logger.info("Error recovery test passed ✓")

@pytest.mark.asyncio
async def test_data_validation(data_manager):
    """Test data validation and cleaning."""
    logger.info("Testing data validation...")
    
    # Test with invalid business name
    with pytest.raises(ValueError):
        await data_manager.get_business_data("")
    
    # Test with special characters
    business_data = await data_manager.get_business_data("Test's & Restaurant")
    assert business_data is not None
    
    # Test review text cleaning
    reviews = await data_manager.get_reviews(TEST_BUSINESS)
    for review in reviews:
        assert len(review["text"]) > 0
        assert not any(char in review["text"] for char in ["<", ">", "{", "}"])
    
    logger.info("Data validation test passed ✓")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
