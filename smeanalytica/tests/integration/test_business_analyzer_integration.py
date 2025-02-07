"""Integration tests for BusinessAnalyzer with real API data.

This module provides comprehensive integration tests for the BusinessAnalyzer
component, ensuring proper functionality with real API data, security measures,
and performance monitoring.
"""

import os
import pytest
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import json

from smeanalytica.core.analyzers.business_analyzer import BusinessAnalyzer
from smeanalytica.core.data.data_source_manager import DataSourceManager
from smeanalytica.shared.restaurant_data_fetcher import RestaurantDataFetcher
from smeanalytica.config.business_types import BusinessType
from smeanalytica.utils.logger import setup_logger
from smeanalytica.utils.performance import PerformanceMonitor
from smeanalytica.utils.security import validate_api_response
from smeanalytica.config.test_config import TestConfig

# Initialize logger
logger = setup_logger(__name__, logging.INFO)
perf_monitor = PerformanceMonitor()

@pytest.fixture(scope="module")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def business_analyzer():
    """Create a BusinessAnalyzer instance for testing."""
    analyzer = BusinessAnalyzer()
    yield analyzer
    await analyzer.close()

@pytest.fixture(scope="module")
def data_source_manager():
    """Create a DataSourceManager instance for testing."""
    return DataSourceManager()

@pytest.fixture(scope="module")
def test_config():
    """Create a TestConfig instance for testing."""
    return TestConfig()

class TestBusinessAnalyzerIntegration:
    """Integration tests for BusinessAnalyzer with real API data."""

    @pytest.mark.asyncio
    async def test_complete_analysis(self, business_analyzer: BusinessAnalyzer, test_config: TestConfig):
        """Test complete business analysis with real API data."""
        test_results = []
        
        for business in test_config.test_businesses:
            with perf_monitor.measure(f"complete_analysis_{business['name']}"):
                logger.info(f"Starting analysis for {business['name']}")
                
                try:
                    result = await business_analyzer.analyze_business(
                        business["name"],
                        business["location"],
                        business["type"]
                    )
                    
                    # Validate response structure and data quality
                    validation_result = self._validate_analysis_result(
                        result,
                        test_config.validation_rules
                    )
                    test_results.append(validation_result)
                    
                    # Log performance metrics
                    perf_stats = perf_monitor.get_stats()
                    logger.info(
                        f"Analysis completed for {business['name']}\n"
                        f"Duration: {perf_stats['duration']:.2f}s\n"
                        f"Memory usage: {perf_stats['memory_usage']:.2f}MB\n"
                        f"API calls: {perf_stats['api_calls']}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Analysis failed for {business['name']}: {str(e)}",
                        exc_info=True
                    )
                    raise
        
        # Generate test report
        self._generate_test_report(test_results, test_config.report_dir)
    
    @pytest.mark.asyncio
    async def test_api_resilience(
        self,
        data_source_manager: DataSourceManager,
        test_config: TestConfig
    ):
        """Test API resilience and fallback mechanisms."""
        test_cases = [
            {
                "scenario": "all_apis_available",
                "disabled_apis": [],
                "expected_success": True
            },
            {
                "scenario": "google_places_down",
                "disabled_apis": ["google_places"],
                "expected_success": True
            },
            {
                "scenario": "yelp_down",
                "disabled_apis": ["yelp"],
                "expected_success": True
            },
            {
                "scenario": "tripadvisor_down",
                "disabled_apis": ["tripadvisor"],
                "expected_success": True
            }
        ]
        
        for test_case in test_cases:
            with perf_monitor.measure(f"api_resilience_{test_case['scenario']}"):
                logger.info(f"Testing scenario: {test_case['scenario']}")
                
                try:
                    # Temporarily disable specified APIs
                    self._disable_apis(data_source_manager, test_case["disabled_apis"])
                    
                    # Test data fetching
                    result = await data_source_manager.get_business_data(
                        test_config.test_businesses[0]["name"],
                        test_config.test_businesses[0]["location"]
                    )
                    
                    # Validate results
                    assert bool(result) == test_case["expected_success"], \
                        f"Unexpected result for scenario {test_case['scenario']}"
                    
                    # Validate API response security
                    if result:
                        validate_api_response(result, test_config.security)
                    
                    logger.info(f"Scenario {test_case['scenario']} passed")
                    
                except Exception as e:
                    logger.error(
                        f"Scenario {test_case['scenario']} failed: {str(e)}",
                        exc_info=True
                    )
                    raise
                finally:
                    # Re-enable all APIs
                    self._enable_all_apis(data_source_manager)
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self,
        business_analyzer: BusinessAnalyzer,
        test_config: TestConfig
    ):
        """Test handling of concurrent analysis requests."""
        with perf_monitor.measure("concurrent_requests"):
            try:
                # Create concurrent analysis tasks
                tasks = []
                for business in test_config.test_businesses[:test_config.batch_size]:
                    task = business_analyzer.analyze_business(
                        business["name"],
                        business["location"],
                        business["type"]
                    )
                    tasks.append(task)
                
                # Run analyses concurrently with timeout
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks),
                    timeout=test_config.timeout
                )
                
                # Validate results
                assert len(results) == len(tasks), "Not all analyses completed"
                for result in results:
                    validate_api_response(result, test_config.security)
                
                # Log performance metrics
                perf_stats = perf_monitor.get_stats()
                logger.info(
                    "Concurrent analysis completed\n"
                    f"Total duration: {perf_stats['duration']:.2f}s\n"
                    f"Average time per analysis: {perf_stats['duration']/len(tasks):.2f}s\n"
                    f"Peak memory usage: {perf_stats['peak_memory']:.2f}MB\n"
                    f"Total API calls: {perf_stats['total_api_calls']}"
                )
                
            except asyncio.TimeoutError:
                logger.error(
                    f"Concurrent analysis timed out after {test_config.timeout}s"
                )
                raise
            except Exception as e:
                logger.error("Concurrent analysis failed", exc_info=True)
                raise
    
    def _validate_analysis_result(
        self,
        result: Dict[str, Any],
        validation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate analysis result structure and data quality."""
        validation = {
            "passed": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate required sections
            required_sections = [
                "business_info",
                "sentiment_analysis",
                "competitor_analysis",
                "recommendations"
            ]
            for section in required_sections:
                if section not in result:
                    validation["passed"] = False
                    validation["errors"].append(f"Missing required section: {section}")
            
            # Validate data quality
            if "business_info" in result:
                self._validate_business_info(
                    result["business_info"],
                    validation_rules.get("business_info", {}),
                    validation
                )
            
            if "sentiment_analysis" in result:
                self._validate_sentiment_analysis(
                    result["sentiment_analysis"],
                    validation_rules.get("sentiment_analysis", {}),
                    validation
                )
            
            if "competitor_analysis" in result:
                self._validate_competitor_analysis(
                    result["competitor_analysis"],
                    validation_rules.get("competitor_analysis", {}),
                    validation
                )
            
        except Exception as e:
            validation["passed"] = False
            validation["errors"].append(f"Validation error: {str(e)}")
            logger.error("Validation failed", exc_info=True)
        
        return validation
    
    def _generate_test_report(
        self,
        test_results: List[Dict[str, Any]],
        report_dir: Path
    ):
        """Generate detailed test report with metrics and findings."""
        try:
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = report_dir / f"test_report_{datetime.now():%Y%m%d_%H%M%S}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(test_results),
                "passed_tests": sum(1 for r in test_results if r["passed"]),
                "performance_metrics": perf_monitor.get_summary(),
                "test_results": test_results
            }
            
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Test report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate test report: {str(e)}")
    
    def _disable_apis(
        self,
        data_source_manager: DataSourceManager,
        apis_to_disable: List[str]
    ):
        """Temporarily disable specified APIs for testing."""
        for api in apis_to_disable:
            if hasattr(data_source_manager, api):
                setattr(getattr(data_source_manager, api), "api_key", "invalid_key")
    
    def _enable_all_apis(self, data_source_manager: DataSourceManager):
        """Re-enable all APIs after testing."""
        data_source_manager.reload_api_keys()
