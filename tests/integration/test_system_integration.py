"""System-wide integration tests for the business analysis system."""

import os
import asyncio
import pytest
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from smeanalytica.solutions.sales_forecast import SalesForecastAnalyzer
from smeanalytica.solutions.simple_forecast import SimpleForecastAnalyzer
from smeanalytica.shared.mock_data_fetcher import MockDataFetcher
from smeanalytica.shared.cache import DataCache
from smeanalytica.utils.performance import PerformanceMonitor
from smeanalytica.config.test_config import TestConfig
from smeanalytica.types.business_type import BusinessType

logger = logging.getLogger(__name__)
performance = PerformanceMonitor()

@asynccontextmanager
async def data_fetcher_context():
    """Create a data fetcher instance."""
    fetcher = MockDataFetcher(business_type=BusinessType.RESTAURANT)
    fetcher = await fetcher.initialize()
    try:
        yield fetcher
    finally:
        await fetcher.cache.shutdown()

@asynccontextmanager
async def cache_context():
    """Create a cache instance."""
    cache = DataCache()
    cache = await cache.initialize()
    try:
        yield cache
    finally:
        await cache.shutdown()

@pytest.fixture
async def data_fetcher():
    """Data fetcher fixture."""
    async with data_fetcher_context() as fetcher:
        yield fetcher

@pytest.fixture
async def cache():
    """Cache fixture."""
    async with cache_context() as cache:
        yield cache

@pytest.mark.asyncio
async def test_end_to_end_analysis(data_fetcher, cache):
    """Test complete business analysis flow."""
    cache = await anext(cache)
    
    test_cases = TestConfig.TEST_BUSINESSES.items()
    
    for business_type, profile in test_cases:
        logger.info(f"Testing {business_type}: {profile.name}")

        # Create a new data fetcher with the correct business type
        async with data_fetcher_context() as test_fetcher:
            test_fetcher.business_type = profile.business_type
            
            # Initialize cache metrics outside performance measurement
            cache_metrics = {
                'cache_hits': cache._hits,
                'cache_misses': cache._misses
            }
            logger.info(f"Initial Cache Status - Hits: {cache_metrics['cache_hits']}, Misses: {cache_metrics['cache_misses']}")

            metrics = {'duration': 0, 'custom_metrics': {}, 'cache_hits': 0, 'cache_misses': 0, 'errors': 0}
            with performance.measure(f"e2e_test_{business_type}") as perf_metrics:
                try:
                    # 1. Data Fetching
                    business_data = await test_fetcher.get_business_data(profile.name)
                    assert business_data, f"No data fetched for {profile.name}"
                    
                    # Validate core business data
                    validation_errors = TestConfig.validate_business_data(business_data)
                    assert not validation_errors, f"Validation errors: {validation_errors}"
                    
                    # 2. Forecasting
                    forecast_analyzer = SalesForecastAnalyzer(test_fetcher, cache)
                    await forecast_analyzer.initialize()
                    forecast_results = await forecast_analyzer.analyze(profile.name)
                    
                    # Validate forecast results
                    assert len(forecast_results['forecast_values']) > 0, "Empty forecast"
                    
                    # Compare with expected metrics
                    actual_metrics = forecast_results['business_metrics']['current_performance']
                    expected = profile.expected_metrics
                    
                    assert actual_metrics['rating'] >= expected['min_rating'], \
                        f"Rating below minimum: {actual_metrics['rating']} < {expected['min_rating']}"
                    assert actual_metrics['reviews_count'] >= expected['min_reviews'], \
                        f"Reviews below minimum: {actual_metrics['reviews_count']} < {expected['min_reviews']}"
                    assert actual_metrics['price_level'] in expected['price_range'], \
                        f"Price level {actual_metrics['price_level']} not in expected range"
                    
                    # 3. Cache Validation
                    cache_key = f"sales_forecast:{profile.name}:{profile.business_type.value.upper()}"
                    logger.debug(f"Retrieving cache entry: {cache_key}")
                    cached_data = await cache.get(cache_key)
                    assert cached_data, "Data not cached properly"
                    
                    # Update cache metrics after operations
                    metrics['cache_hits'] = cache._hits - cache_metrics['cache_hits']
                    metrics['cache_misses'] = cache._misses - cache_metrics['cache_misses']
                    
                    # Record metrics
                    perf_metrics['custom_metrics'].update({
                        'data_fetch_time': perf_metrics['duration'],
                        'cache_hit_rate': metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses']),
                        'api_errors': perf_metrics.get('errors', 0),
                        'validation_errors': len(validation_errors),
                        'test_case': business_type,
                        'profile_name': profile.name
                    })
                    
                    logger.info(f"Final Cache Status - Hits: {metrics['cache_hits']}, Misses: {metrics['cache_misses']}")

                except Exception as e:
                    logger.error(f"Test failed for {profile.name}: {str(e)}")
                    raise

@pytest.mark.asyncio
async def test_concurrent_requests(data_fetcher):
    """Test system performance under concurrent load."""
    data_fetcher = await anext(data_fetcher)
    
    test_cases = list(TestConfig.TEST_BUSINESSES.values())[:3]  # Test with first 3 businesses
    concurrent_requests = 5
    
    metrics = {'duration': 0, 'custom_metrics': {}, 'cache_hits': 0, 'cache_misses': 0, 'errors': 0}
    logger.info(f"Cache Status - Hits: {metrics['cache_hits']}, Misses: {metrics['cache_misses']}")
    with performance.measure("concurrent_requests") as metrics:
        try:
            # Create multiple concurrent requests
            tasks = []
            for _ in range(concurrent_requests):
                for profile in test_cases:
                    task = data_fetcher.get_business_data(profile.name)
                    tasks.append(task)
            
            # Execute concurrent requests
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Validate results
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            error_count = len(results) - success_count
            
            metrics['custom_metrics'].update({
                'total_requests': len(results),
                'successful_requests': success_count,
                'failed_requests': error_count,
                'average_response_time': metrics['duration'] / len(results),
                'test_type': 'concurrent_requests'
            })
            
            # Assert performance criteria
            assert metrics['duration'] / len(results) <= TestConfig.PERFORMANCE_BENCHMARKS['api_response_time'], \
                "Average response time exceeds benchmark"
            assert error_count / len(results) <= TestConfig.PERFORMANCE_BENCHMARKS['max_api_errors'], \
                "Error rate exceeds benchmark"
            
        except Exception as e:
            logger.error(f"Concurrent request test failed: {str(e)}")
            raise

@pytest.mark.asyncio
async def test_error_handling(data_fetcher):
    """Test system behavior with various error conditions."""
    data_fetcher = await anext(data_fetcher)
    
    test_cases = [
        {'name': 'NonexistentBusiness123', 'should_fail': True},
        {'name': 'Invalid!@#$Name', 'should_fail': True},
        {'name': '', 'should_fail': True},
        {'name': 'La Riua', 'should_fail': False}  # Known good case
    ]
    
    for test_case in test_cases:
        metrics = {'duration': 0, 'custom_metrics': {}, 'cache_hits': 0, 'cache_misses': 0, 'errors': 0}
        logger.info(f"Cache Status - Hits: {metrics['cache_hits']}, Misses: {metrics['cache_misses']}")
        with performance.measure(f"error_test_{test_case['name']}") as metrics:
            try:
                result = await data_fetcher.get_business_data(test_case['name'])
                
                if test_case['should_fail']:
                    assert not result, f"Expected failure for {test_case['name']}"
                else:
                    assert result, f"Expected success for {test_case['name']}"
                    
                metrics['custom_metrics'].update({
                    'test_case': test_case['name'],
                    'should_fail': test_case['should_fail'],
                    'result': result
                })
                
            except Exception as e:
                if not test_case['should_fail']:
                    raise
                logger.info(f"Expected error for {test_case['name']}: {str(e)}")

@pytest.mark.asyncio
async def test_cache_efficiency(data_fetcher, cache):
    """Test cache performance and data freshness."""
    data_fetcher = await anext(data_fetcher)
    cache = await anext(cache)
    
    test_profile = TestConfig.TEST_BUSINESSES['restaurant']
    
    metrics = {'duration': 0, 'custom_metrics': {}, 'cache_hits': 0, 'cache_misses': 0, 'errors': 0}
    metrics['cache_hits'] = cache._hits
    metrics['cache_misses'] = cache._misses
    logger.info(f"Cache Status - Hits: {metrics['cache_hits']}, Misses: {metrics['cache_misses']}")
    with performance.measure("cache_efficiency") as metrics:
        try:
            # First request - should miss cache
            t1_start = datetime.now()
            result1 = await data_fetcher.get_business_data(test_profile.name)
            t1_duration = (datetime.now() - t1_start).total_seconds()
            
            # Second request - should hit cache
            t2_start = datetime.now()
            result2 = await data_fetcher.get_business_data(test_profile.name)
            t2_duration = (datetime.now() - t2_start).total_seconds()
            
            # Validate cache hit was faster
            assert t2_duration < t1_duration, "Cache hit not faster than miss"
            
            # Validate data consistency
            assert result1 == result2, "Cached data differs from original"
            
            metrics['custom_metrics'].update({
                'first_request_time': t1_duration,
                'cache_hit_time': t2_duration,
                'time_saved': t1_duration - t2_duration,
                'test_type': 'cache_efficiency'
            })
            
        except Exception as e:
            logger.error(f"Cache efficiency test failed: {str(e)}")
            raise

def test_seasonal_adjustments():
    """Test seasonal adjustment calculations."""
    test_cases = [
        (BusinessType.RESTAURANT, 7, 1.4),  # July - peak season
        (BusinessType.HOTEL, 1, 0.8),      # January - low season
        (BusinessType.RETAIL, 12, 1.5),    # December - holiday season
        (BusinessType.ENTERTAINMENT, 8, 1.4),  # August - summer
        (BusinessType.WELLNESS, 1, 1.3)    # January - New Year resolutions
    ]
    
    for business_type, month, expected_factor in test_cases:
        analyzer = SimpleForecastAnalyzer(business_type)
        factor = analyzer.apply_seasonal_adjustment(100, month) / 100
        assert abs(factor - expected_factor) < 0.01, \
            f"Incorrect seasonal factor for {business_type} in month {month}"
