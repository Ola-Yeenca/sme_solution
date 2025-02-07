"""Performance testing suite for the business analysis system."""

import os
import asyncio
import pytest
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
import psutil
import statistics

from smeanalytica.solutions.sales_forecast import SalesForecastAnalyzer
from smeanalytica.shared.restaurant_data_fetcher import RestaurantDataFetcher
from smeanalytica.shared.cache import DataCache
from smeanalytica.utils.performance import PerformanceMonitor
from smeanalytica.config.test_config import TestConfig

logger = logging.getLogger(__name__)
performance = PerformanceMonitor()

class PerformanceTest:
    """Performance test suite with metrics collection."""
    
    def __init__(self):
        """Initialize performance test suite."""
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'api_errors': 0,
            'concurrent_requests': 0
        }
        self.start_time = None
        self.process = psutil.Process()
    
    def start_test(self):
        """Start a test run."""
        self.start_time = time.time()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def end_test(self):
        """End a test run and calculate metrics."""
        duration = time.time() - self.start_time
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - self.initial_memory
        
        self.metrics['memory_usage'].append(memory_increase)
        
        return {
            'duration': duration,
            'avg_response_time': statistics.mean(self.metrics['response_times']),
            'p95_response_time': statistics.quantiles(self.metrics['response_times'], n=20)[18],
            'memory_increase_mb': memory_increase,
            'cache_hit_rate': self.metrics['cache_hits'] / 
                (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0,
            'error_rate': self.metrics['api_errors'] / self.metrics['concurrent_requests']
                if self.metrics['concurrent_requests'] > 0 else 0
        }

@pytest.fixture
async def performance_test():
    """Create performance test instance."""
    return PerformanceTest()

@pytest.fixture
async def data_fetcher():
    """Create data fetcher instance."""
    return RestaurantDataFetcher()

@pytest.mark.asyncio
async def test_load_performance(performance_test, data_fetcher):
    """Test system performance under load."""
    concurrent_users = [1, 5, 10, 20]  # Test with increasing concurrent users
    requests_per_user = 5
    test_businesses = list(TestConfig.TEST_BUSINESSES.values())
    
    results = {}
    for num_users in concurrent_users:
        performance_test.start_test()
        
        try:
            # Create tasks for each user
            tasks = []
            for _ in range(num_users):
                for _ in range(requests_per_user):
                    for business in test_businesses:
                        task = data_fetcher.get_business_data(business.name)
                        tasks.append(task)
            
            performance_test.metrics['concurrent_requests'] = len(tasks)
            
            # Execute requests with timing
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Calculate metrics
            response_time = (end_time - start_time) / len(tasks)
            performance_test.metrics['response_times'].append(response_time)
            
            # Count errors
            errors = sum(1 for r in responses if isinstance(r, Exception))
            performance_test.metrics['api_errors'] += errors
            
            # Get test results
            results[num_users] = performance_test.end_test()
            
            # Validate against benchmarks
            assert results[num_users]['avg_response_time'] <= \
                TestConfig.PERFORMANCE_BENCHMARKS['api_response_time'], \
                f"Response time too high for {num_users} users"
            
            assert results[num_users]['error_rate'] <= \
                TestConfig.PERFORMANCE_BENCHMARKS['max_api_errors'], \
                f"Error rate too high for {num_users} users"
            
            assert results[num_users]['memory_increase_mb'] <= \
                TestConfig.PERFORMANCE_BENCHMARKS['max_memory_usage'], \
                f"Memory usage too high for {num_users} users"
            
        except Exception as e:
            logger.error(f"Load test failed for {num_users} users: {str(e)}")
            raise
        
        # Allow system to stabilize between tests
        await asyncio.sleep(2)
    
    return results

@pytest.mark.asyncio
async def test_cache_performance(performance_test, data_fetcher):
    """Test cache performance and efficiency."""
    test_iterations = 50
    test_business = TestConfig.TEST_BUSINESSES['restaurant']
    
    performance_test.start_test()
    
    try:
        # Warm up cache
        await data_fetcher.get_business_data(test_business.name)
        
        # Test cache hits
        for _ in range(test_iterations):
            start_time = time.time()
            result = await data_fetcher.get_business_data(test_business.name)
            response_time = time.time() - start_time
            
            performance_test.metrics['response_times'].append(response_time)
            if result:
                performance_test.metrics['cache_hits'] += 1
            else:
                performance_test.metrics['cache_misses'] += 1
        
        results = performance_test.end_test()
        
        # Validate cache performance
        assert results['cache_hit_rate'] >= \
            TestConfig.PERFORMANCE_BENCHMARKS['cache_hit_rate'], \
            "Cache hit rate below benchmark"
        
        assert results['avg_response_time'] <= \
            TestConfig.PERFORMANCE_BENCHMARKS['api_response_time'] * 0.5, \
            "Cache response time too slow"
        
    except Exception as e:
        logger.error(f"Cache performance test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_memory_leaks(performance_test, data_fetcher):
    """Test for memory leaks during extended operation."""
    test_iterations = 100
    test_business = TestConfig.TEST_BUSINESSES['restaurant']
    
    performance_test.start_test()
    initial_memory = performance_test.initial_memory
    
    try:
        for i in range(test_iterations):
            # Perform operations
            await data_fetcher.get_business_data(test_business.name)
            
            # Record memory usage
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            performance_test.metrics['memory_usage'].append(current_memory)
            
            # Check for significant memory growth
            if i > 10:  # Allow for initial memory allocation
                memory_growth = current_memory - initial_memory
                assert memory_growth <= \
                    TestConfig.PERFORMANCE_BENCHMARKS['max_memory_usage'], \
                    f"Potential memory leak detected: {memory_growth}MB increase"
            
            # Brief pause to allow for garbage collection
            await asyncio.sleep(0.1)
        
    except Exception as e:
        logger.error(f"Memory leak test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_error_recovery(performance_test, data_fetcher):
    """Test system recovery from errors and failures."""
    test_cases = [
        {'name': 'NonexistentBusiness', 'delay': 0},
        {'name': 'La Riua', 'delay': 0.1},
        {'name': 'Invalid@Business', 'delay': 0},
        {'name': 'La Riua', 'delay': 0}
    ]
    
    performance_test.start_test()
    
    try:
        for case in test_cases:
            start_time = time.time()
            try:
                await data_fetcher.get_business_data(case['name'])
                performance_test.metrics['response_times'].append(time.time() - start_time)
            except Exception as e:
                performance_test.metrics['api_errors'] += 1
            
            await asyncio.sleep(case['delay'])
        
        results = performance_test.end_test()
        
        # Validate error handling
        assert results['error_rate'] <= \
            TestConfig.PERFORMANCE_BENCHMARKS['max_api_errors'], \
            "Error recovery not working properly"
        
    except Exception as e:
        logger.error(f"Error recovery test failed: {str(e)}")
        raise
