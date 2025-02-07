"""Tests for DeepSeek AI integration."""

import pytest
import json
from unittest.mock import Mock, patch
from smeanalytica.shared.deepseek_client import DeepSeekClient
from smeanalytica.core.pricing.pricing_engine import DynamicPricingEngine

@pytest.fixture
async def deepseek_client():
    """Create a DeepSeek client for testing."""
    client = DeepSeekClient()
    yield client
    await client.close()

@pytest.fixture
async def pricing_engine():
    """Create a pricing engine for testing."""
    engine = DynamicPricingEngine()
    yield engine
    await engine.close()

@pytest.fixture
def global_business_samples():
    """Sample business data from different regions."""
    return [
        {
            "name": "Valencia Restaurant",
            "type": "restaurant",
            "location": "Valencia, Comunidad Valenciana, Spain",
            "metrics": {
                "avg_monthly_revenue": 50000,
                "customer_count": 1000
            }
        },
        {
            "name": "NYC Deli",
            "type": "restaurant",
            "location": "Manhattan, New York, United States",
            "metrics": {
                "avg_monthly_revenue": 75000,
                "customer_count": 1500
            }
        },
        {
            "name": "London Pub",
            "type": "bar",
            "location": "Westminster, London, United Kingdom",
            "metrics": {
                "avg_monthly_revenue": 65000,
                "customer_count": 1200
            }
        },
        {
            "name": "Tokyo Sushi",
            "type": "restaurant",
            "location": "Shibuya, Tokyo, Japan",
            "metrics": {
                "avg_monthly_revenue": 80000,
                "customer_count": 2000
            }
        }
    ]

@pytest.fixture
def global_market_samples():
    """Sample market data from different regions."""
    return [
        {
            "market_size": 1000000,
            "growth_rate": 0.05,
            "trends": ["increasing_demand", "health_conscious"],
            "seasonality": {
                "high_season": ["summer", "winter"],
                "low_season": ["spring", "fall"]
            },
            "regulations": {
                "food_safety": "EU standards",
                "licensing": "Local municipality"
            }
        },
        {
            "market_size": 2000000,
            "growth_rate": 0.08,
            "trends": ["fast_casual", "delivery_focus"],
            "seasonality": {
                "high_season": ["winter", "spring"],
                "low_season": ["summer", "fall"]
            },
            "regulations": {
                "food_safety": "FDA standards",
                "licensing": "State and city"
            }
        }
    ]

@pytest.fixture
def sample_business_data():
    """Sample business data for testing."""
    return {
        "name": "Test Restaurant",
        "type": "restaurant",
        "location": "Valencia, Spain",
        "metrics": {
            "avg_monthly_revenue": 50000,
            "customer_count": 1000
        }
    }

@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "market_size": 1000000,
        "growth_rate": 0.05,
        "trends": ["increasing_demand", "health_conscious"],
        "seasonality": {
            "high_season": ["summer", "winter"],
            "low_season": ["spring", "fall"]
        }
    }

@pytest.fixture
def sample_competitor_data():
    """Sample competitor data for testing."""
    return {
        "competitors": [
            {
                "name": "Competitor 1",
                "price_range": {"min": 10, "max": 30},
                "rating": 4.5
            },
            {
                "name": "Competitor 2",
                "price_range": {"min": 15, "max": 35},
                "rating": 4.2
            }
        ],
        "avg_price": 22.5,
        "price_distribution": {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.3
        }
    }

@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "sentiment": {
            "positive": 0.7,
            "neutral": 0.2,
            "negative": 0.1
        },
        "price_sensitivity": "medium",
        "preferences": ["quality", "ambiance", "service"]
    }

@pytest.mark.asyncio
async def test_deepseek_client_initialization(deepseek_client):
    """Test DeepSeek client initialization."""
    assert deepseek_client.base_url == "https://api.deepseek.com/v1"
    assert deepseek_client.session is None

@pytest.mark.asyncio
async def test_pricing_analysis_success(
    deepseek_client,
    sample_business_data,
    sample_market_data,
    sample_competitor_data,
    sample_customer_data
):
    """Test successful pricing analysis."""
    mock_response = {
        "pricing_analysis": {
            "suggested_price": 25.0,
            "min_price": 20.0,
            "max_price": 30.0,
            "confidence": 0.85,
            "insights": ["Competitive pricing", "Good margin potential"],
            "market_factors": {"demand": "high", "competition": "medium"},
            "competitor_insights": {"position": "mid-range"},
            "customer_feedback": {"satisfaction": "high"},
            "detected_costs": {"ingredients": 8.0, "labor": 6.0},
            "margin_analysis": {"optimal_margin": 0.35}
        }
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = Mock(
            return_value=mock_response
        )
        
        result = await deepseek_client.analyze_pricing(
            sample_business_data,
            sample_market_data,
            sample_competitor_data,
            sample_customer_data
        )
        
        assert result is not None
        assert result["suggested_price"] == 25.0
        assert result["confidence_score"] == 0.85
        assert len(result["insights"]) > 0

@pytest.mark.asyncio
async def test_pricing_analysis_api_error(
    deepseek_client,
    sample_business_data,
    sample_market_data,
    sample_competitor_data,
    sample_customer_data
):
    """Test handling of API errors."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 500
        mock_post.return_value.__aenter__.return_value.text = Mock(
            return_value="Internal server error"
        )
        
        result = await deepseek_client.analyze_pricing(
            sample_business_data,
            sample_market_data,
            sample_competitor_data,
            sample_customer_data
        )
        
        assert result is None

@pytest.mark.asyncio
async def test_pricing_engine_integration(
    pricing_engine,
    sample_business_data,
    sample_market_data,
    sample_competitor_data,
    sample_customer_data
):
    """Test pricing engine integration with DeepSeek."""
    mock_model = {"name": "test_model", "version": "1.0"}
    
    mock_response = {
        "pricing_analysis": {
            "suggested_price": 25.0,
            "min_price": 20.0,
            "max_price": 30.0,
            "confidence": 0.85,
            "insights": ["Competitive pricing", "Good margin potential"],
            "market_factors": {"demand": "high", "competition": "medium"},
            "competitor_insights": {"position": "mid-range"},
            "customer_feedback": {"satisfaction": "high"},
            "detected_costs": {"ingredients": 8.0, "labor": 6.0},
            "margin_analysis": {"optimal_margin": 0.35}
        }
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = Mock(
            return_value=mock_response
        )
        
        result = await pricing_engine.get_autonomous_recommendation(
            sample_business_data,
            sample_market_data,
            sample_competitor_data,
            sample_customer_data,
            mock_model
        )
        
        assert result is not None
        assert "suggested_price" in result
        assert "market_context" in result
        assert "implementation_steps" in result
        assert len(result["implementation_steps"]) == 3

@pytest.mark.asyncio
async def test_invalid_recommendation_handling(pricing_engine):
    """Test handling of invalid recommendations."""
    mock_model = {"name": "test_model", "version": "1.0"}
    
    # Missing required fields
    invalid_response = {
        "pricing_analysis": {
            "suggested_price": 25.0  # Missing other required fields
        }
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = Mock(
            return_value=invalid_response
        )
        
        result = await pricing_engine.get_autonomous_recommendation(
            {},  # Empty data for this test
            {},
            {},
            {},
            mock_model
        )
        
        assert result is None  # Should fail validation

@pytest.mark.asyncio
async def test_global_pricing_analysis(
    deepseek_client,
    global_business_samples,
    global_market_samples
):
    """Test pricing analysis for businesses in different regions."""
    for business in global_business_samples:
        mock_response = {
            "pricing_analysis": {
                "suggested_price": 25.0,
                "min_price": 20.0,
                "max_price": 30.0,
                "confidence": 0.85,
                "insights": ["Competitive pricing", "Good margin potential"],
                "market_factors": {"demand": "high", "competition": "medium"},
                "competitor_insights": {"position": "mid-range"},
                "customer_feedback": {"satisfaction": "high"},
                "detected_costs": {"ingredients": 8.0, "labor": 6.0},
                "margin_analysis": {"optimal_margin": 0.35},
                "regional_context": {
                    "market_type": "urban",
                    "economic_indicators": {
                        "gdp_growth": 0.02,
                        "inflation": 0.03
                    }
                },
                "currency": "EUR" if "Spain" in business["location"] else (
                    "USD" if "United States" in business["location"] else (
                        "GBP" if "United Kingdom" in business["location"] else "JPY"
                    )
                )
            }
        }
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = Mock(
                return_value=mock_response
            )
            
            result = await deepseek_client.analyze_pricing(
                business,
                global_market_samples[0],
                {"competitors": []},
                {"sentiment": {"positive": 0.7}}
            )
            
            assert result is not None
            assert "regional_context" in result
            assert "currency" in result
            
            # Verify currency is appropriate for region
            if "Spain" in business["location"]:
                assert result["currency"] == "EUR"
            elif "United States" in business["location"]:
                assert result["currency"] == "USD"
            elif "United Kingdom" in business["location"]:
                assert result["currency"] == "GBP"
            elif "Japan" in business["location"]:
                assert result["currency"] == "JPY"

@pytest.mark.asyncio
async def test_region_info_extraction(deepseek_client):
    """Test extraction of regional information."""
    test_locations = [
        {
            "input": "Valencia, Comunidad Valenciana, Spain",
            "expected": {
                "city": "Valencia",
                "region": "Comunidad Valenciana",
                "country": "Spain"
            }
        },
        {
            "input": "Manhattan, New York, United States",
            "expected": {
                "city": "Manhattan",
                "region": "New York",
                "country": "United States"
            }
        },
        {
            "input": "Tokyo, Japan",
            "expected": {
                "city": "Tokyo",
                "country": "Japan",
                "region": ""
            }
        }
    ]
    
    for test_case in test_locations:
        result = deepseek_client._extract_region_info({"location": test_case["input"]})
        assert result["city"] == test_case["expected"]["city"]
        assert result["country"] == test_case["expected"]["country"]
        if "region" in test_case["expected"]:
            assert result["region"] == test_case["expected"]["region"]

@pytest.mark.asyncio
async def test_currency_detection(deepseek_client):
    """Test currency detection for different regions."""
    test_cases = [
        {"location": "Valencia, Spain", "expected": "EUR"},
        {"location": "New York, United States", "expected": "USD"},
        {"location": "London, United Kingdom", "expected": "GBP"},
        {"location": "Unknown Location", "expected": "USD"}  # Default case
    ]
    
    for test_case in test_cases:
        result = deepseek_client._detect_currency({"location": test_case["location"]})
        assert result == test_case["expected"] 