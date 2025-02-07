"""Integration tests for BusinessAnalyzer."""

import os
import pytest
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from smeanalytica.core.analyzers.business_analyzer import BusinessAnalyzer
from smeanalytica.core.models.model_manager import ModelManager
from smeanalytica.core.data.data_source_manager import DataSourceManager
from smeanalytica.core.models.ai_integrations import AIModelIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
SAMPLE_BUSINESS = "Test Restaurant"
SAMPLE_BUSINESS_DATA = {
    "name": "Test Restaurant",
    "rating": 4.5,
    "review_count": 150,
    "price_level": "$$",
    "current_price": 25.99,
    "capacity": 80,
    "established_date": "2020-01-01",
    "amenities": ["wifi", "parking", "outdoor_seating"]
}

SAMPLE_COMPETITORS = [
    {
        "name": "Competitor 1",
        "rating": 4.2,
        "review_count": 120,
        "price": 22.99
    },
    {
        "name": "Competitor 2",
        "rating": 4.7,
        "review_count": 200,
        "price": 28.99
    }
]

SAMPLE_REVIEWS = [
    {
        "rating": 5,
        "text": "Amazing food and great service! Will definitely come back.",
        "date": "2025-01-01"
    },
    {
        "rating": 3,
        "text": "Food was good but service was slow during peak hours.",
        "date": "2025-01-15"
    }
]

SAMPLE_HISTORICAL_DATA = {
    "sales": [
        {"date": "2024-01-01", "sales": 1500},
        {"date": "2024-01-02", "sales": 1800},
        {"date": "2024-01-03", "sales": 1600}
    ]
}

@pytest.fixture
async def analyzer():
    """Create a BusinessAnalyzer instance for testing."""
    model_config = {
        "model": "test_model",
        "config": {"test": True}
    }
    analyzer = BusinessAnalyzer(model_config, business_type="restaurant")
    
    # Mock data manager
    analyzer.data_manager = MagicMock(spec=DataSourceManager)
    analyzer.data_manager.get_business_data.return_value = SAMPLE_BUSINESS_DATA
    analyzer.data_manager.get_competitors.return_value = SAMPLE_COMPETITORS
    analyzer.data_manager.get_reviews.return_value = SAMPLE_REVIEWS
    analyzer.data_manager.get_historical_data.return_value = SAMPLE_HISTORICAL_DATA
    
    # Mock model manager
    analyzer.model_manager = MagicMock(spec=ModelManager)
    analyzer.model_manager.get_model.return_value = {"model": "test_model"}
    
    # Mock AI integration
    analyzer.ai_integration = MagicMock(spec=AIModelIntegration)
    
    return analyzer

@pytest.mark.asyncio
async def test_sentiment_analysis(analyzer):
    """Test sentiment analysis functionality."""
    logger.info("Testing sentiment analysis...")
    
    # Mock Claude-3 response
    analyzer.ai_integration.get_claude_analysis.return_value = MagicMock(
        content={
            "sentiment": "positive",
            "score": 0.85,
            "confidence": 0.92,
            "themes": ["food quality", "service"],
            "summary": "Generally positive reviews with some service concerns"
        }
    )
    
    # Run analysis
    result = await analyzer.analyze(SAMPLE_BUSINESS, "sentiment")
    
    # Validate response structure
    assert "business" in result
    assert "analysis_type" in result
    assert "result" in result
    assert "confidence" in result
    assert "timestamp" in result
    
    # Validate sentiment analysis
    sentiment_result = result["result"]
    assert "sentiment" in sentiment_result
    assert "score" in sentiment_result
    assert "themes" in sentiment_result
    assert isinstance(sentiment_result["themes"], list)
    
    logger.info("Sentiment analysis test passed ✓")

@pytest.mark.asyncio
async def test_pricing_analysis(analyzer):
    """Test pricing analysis functionality."""
    logger.info("Testing pricing analysis...")
    
    # Run analysis
    result = await analyzer.analyze(SAMPLE_BUSINESS, "pricing")
    
    # Validate response structure
    assert "business" in result
    assert "analysis_type" in result
    assert "result" in result
    
    # Validate pricing analysis
    pricing_result = result["result"]
    assert "recommended_price" in pricing_result
    assert "price_range" in pricing_result
    assert "market_position" in pricing_result
    assert "competitor_analysis" in pricing_result
    
    # Validate price calculations
    assert pricing_result["recommended_price"] > 0
    assert pricing_result["price_range"]["min"] < pricing_result["price_range"]["max"]
    
    logger.info("Pricing analysis test passed ✓")

@pytest.mark.asyncio
async def test_competitor_analysis(analyzer):
    """Test competitor analysis functionality."""
    logger.info("Testing competitor analysis...")
    
    # Mock GPT-4 response
    analyzer.ai_integration.get_gpt4_analysis.return_value = MagicMock(
        content={
            "market_position": "mid-market",
            "advantages": ["location", "unique menu"],
            "opportunities": ["delivery service", "catering"],
            "threats": ["new competitors", "rising costs"],
            "recommendations": ["expand menu", "improve service"],
            "confidence": 0.88
        }
    )
    
    # Run analysis
    result = await analyzer.analyze(SAMPLE_BUSINESS, "competitors")
    
    # Validate response structure
    assert "business" in result
    assert "analysis_type" in result
    assert "result" in result
    
    # Validate competitor analysis
    competitor_result = result["result"]
    assert "market_position" in competitor_result
    assert "competitive_advantages" in competitor_result
    assert "opportunities" in competitor_result
    assert "threats" in competitor_result
    assert "recommendations" in competitor_result
    
    logger.info("Competitor analysis test passed ✓")

@pytest.mark.asyncio
async def test_forecast_analysis(analyzer):
    """Test sales forecasting functionality."""
    logger.info("Testing sales forecasting...")
    
    # Mock Mistral response
    analyzer.ai_integration.get_mistral_analysis.return_value = MagicMock(
        content={
            "trends": ["seasonal peaks", "steady growth"],
            "seasonality": {"summer": "high", "winter": "low"},
            "contributing_factors": ["weather", "events"]
        }
    )
    
    # Run analysis
    result = await analyzer.analyze(SAMPLE_BUSINESS, "forecast")
    
    # Validate response structure
    assert "business" in result
    assert "analysis_type" in result
    assert "result" in result
    
    # Validate forecast analysis
    forecast_result = result["result"]
    assert "forecast" in forecast_result
    assert "trends" in forecast_result
    assert "seasonality" in forecast_result
    assert "growth_rate" in forecast_result
    
    # Validate forecast values
    forecast = forecast_result["forecast"]
    assert "next_month" in forecast
    assert "next_quarter" in forecast
    assert "next_year" in forecast
    assert all(isinstance(v, (int, float)) for v in forecast.values())
    
    logger.info("Forecast analysis test passed ✓")

@pytest.mark.asyncio
async def test_error_handling(analyzer):
    """Test error handling and fallback mechanisms."""
    logger.info("Testing error handling...")
    
    # Test missing business data
    analyzer.data_manager.get_business_data.side_effect = Exception("API Error")
    
    with pytest.raises(RuntimeError) as exc_info:
        await analyzer.analyze(SAMPLE_BUSINESS, "sentiment")
    assert "Analysis failed" in str(exc_info.value)
    
    # Test invalid analysis type
    with pytest.raises(ValueError) as exc_info:
        await analyzer.analyze(SAMPLE_BUSINESS, "invalid_type")
    assert "Unsupported analysis type" in str(exc_info.value)
    
    logger.info("Error handling test passed ✓")

@pytest.mark.asyncio
async def test_performance(analyzer):
    """Test analysis performance."""
    logger.info("Testing performance...")
    
    # Measure response time for each analysis type
    analysis_types = ["sentiment", "pricing", "competitors", "forecast"]
    response_times = {}
    
    for analysis_type in analysis_types:
        start_time = datetime.now()
        await analyzer.analyze(SAMPLE_BUSINESS, analysis_type)
        duration = (datetime.now() - start_time).total_seconds()
        response_times[analysis_type] = duration
        
        # Assert reasonable response time (< 5 seconds)
        assert duration < 5, f"{analysis_type} analysis took too long: {duration}s"
    
    logger.info("Performance test passed ✓")
    logger.info("Response times: %s", json.dumps(response_times, indent=2))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
