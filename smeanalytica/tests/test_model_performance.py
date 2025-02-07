"""Performance tests for AI models and predictions."""

import os
import pytest
import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from smeanalytica.core.models.model_manager import ModelManager
from smeanalytica.core.models.ai_integrations import AIModelIntegration
from smeanalytica.core.models.feature_engineering import FeatureEngineering

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
SAMPLE_REVIEWS = pd.read_csv("tests/data/sample_reviews.csv")
HISTORICAL_SALES = pd.read_csv("tests/data/historical_sales.csv")
COMPETITOR_DATA = pd.read_csv("tests/data/competitor_data.csv")

@pytest.fixture
def model_manager():
    """Create a ModelManager instance for testing."""
    return ModelManager()

@pytest.fixture
def ai_integration():
    """Create an AIModelIntegration instance for testing."""
    return AIModelIntegration()

@pytest.fixture
def feature_engineering():
    """Create a FeatureEngineering instance for testing."""
    return FeatureEngineering()

@pytest.mark.asyncio
async def test_sentiment_model_accuracy(ai_integration):
    """Test sentiment analysis model accuracy."""
    logger.info("Testing sentiment model accuracy...")
    
    # Load labeled test data
    labeled_reviews = SAMPLE_REVIEWS[SAMPLE_REVIEWS["label"].notna()]
    
    correct_predictions = 0
    total_predictions = len(labeled_reviews)
    
    for _, review in labeled_reviews.iterrows():
        response = await ai_integration.get_claude_analysis(
            "Analyze the sentiment of this review.",
            review["text"]
        )
        
        predicted = response.content["sentiment"]
        actual = review["label"]
        
        if predicted == actual:
            correct_predictions += 1
    
    accuracy = correct_predictions / total_predictions
    assert accuracy >= 0.85, f"Sentiment analysis accuracy ({accuracy:.2%}) below threshold"
    
    logger.info("Sentiment model accuracy: %.2f%%", accuracy * 100)
    logger.info("Sentiment model test passed ✓")

@pytest.mark.asyncio
async def test_pricing_model_accuracy(feature_engineering):
    """Test pricing model predictions."""
    logger.info("Testing pricing model accuracy...")
    
    # Load test data
    test_data = COMPETITOR_DATA[COMPETITOR_DATA["actual_price"].notna()]
    
    predictions = []
    actuals = []
    
    for _, row in test_data.iterrows():
        # Prepare features
        business_data = {
            "rating": row["rating"],
            "review_count": row["review_count"],
            "capacity": row["capacity"],
            "current_price": row["current_price"]
        }
        
        competitors = json.loads(row["competitor_data"])
        features = feature_engineering.prepare_pricing_features(business_data, competitors)
        
        # Make prediction
        model_path = "models/pricing_model.json"
        model = xgb.Booster()
        model.load_model(model_path)
        
        prediction = model.predict(xgb.DMatrix(features))[0]
        actual = row["actual_price"]
        
        predictions.append(prediction)
        actuals.append(actual)
    
    # Calculate metrics
    mape = np.mean(np.abs((np.array(actuals) - np.array(predictions)) / np.array(actuals))) * 100
    assert mape <= 15, f"Pricing model MAPE ({mape:.2f}%) above threshold"
    
    logger.info("Pricing model MAPE: %.2f%%", mape)
    logger.info("Pricing model test passed ✓")

@pytest.mark.asyncio
async def test_forecast_model_accuracy(feature_engineering):
    """Test sales forecasting accuracy."""
    logger.info("Testing forecast model accuracy...")
    
    # Load historical data
    df = HISTORICAL_SALES.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    # Split into training and testing
    train_data = df[df["date"] < "2025-01-01"]
    test_data = df[df["date"] >= "2025-01-01"]
    
    # Prepare features
    features = feature_engineering.prepare_forecast_features({"sales": train_data.to_dict("records")})
    
    # Make predictions
    model = xgb.Booster()
    model.load_model("models/forecast_model.json")
    predictions = model.predict(xgb.DMatrix(features))
    
    # Calculate metrics
    mape = np.mean(np.abs((test_data["sales"].values - predictions) / test_data["sales"].values)) * 100
    assert mape <= 20, f"Forecast model MAPE ({mape:.2f}%) above threshold"
    
    logger.info("Forecast model MAPE: %.2f%%", mape)
    logger.info("Forecast model test passed ✓")

@pytest.mark.asyncio
async def test_competitor_analysis_quality(ai_integration):
    """Test competitor analysis quality and consistency."""
    logger.info("Testing competitor analysis quality...")
    
    # Test data
    business_data = {
        "name": "Test Restaurant",
        "rating": 4.5,
        "price_level": "$$"
    }
    competitors = COMPETITOR_DATA.head(5).to_dict("records")
    
    # Get multiple analyses
    analyses = []
    for _ in range(3):
        response = await ai_integration.get_gpt4_analysis(
            "Analyze the competitive landscape.",
            {
                "business": business_data,
                "competitors": competitors
            }
        )
        analyses.append(response.content)
    
    # Check consistency
    key_metrics = ["market_position", "competitive_advantages", "threats"]
    for metric in key_metrics:
        values = [analysis[metric] for analysis in analyses]
        # Check if at least 2 out of 3 analyses agree
        assert any(values.count(x) >= 2 for x in values), f"Inconsistent {metric} analysis"
    
    logger.info("Competitor analysis quality test passed ✓")

@pytest.mark.asyncio
async def test_model_response_times():
    """Test model response times under load."""
    logger.info("Testing model response times...")
    
    ai = AIModelIntegration()
    test_prompt = "Test prompt"
    test_data = {"test": "data"}
    
    async def time_model_call(model_func, *args):
        start = datetime.now()
        await model_func(*args)
        return (datetime.now() - start).total_seconds()
    
    # Test each model
    models = {
        "Claude-3": ai.get_claude_analysis,
        "GPT-4": ai.get_gpt4_analysis,
        "Mistral": ai.get_mistral_analysis
    }
    
    response_times = {}
    for model_name, model_func in models.items():
        times = []
        for _ in range(3):
            time = await time_model_call(model_func, test_prompt, test_data)
            times.append(time)
        
        avg_time = np.mean(times)
        assert avg_time < 5, f"{model_name} average response time ({avg_time:.2f}s) too high"
        response_times[model_name] = avg_time
    
    logger.info("Model response times: %s", json.dumps(response_times, indent=2))
    logger.info("Response time test passed ✓")

@pytest.mark.asyncio
async def test_concurrent_model_calls():
    """Test concurrent model execution."""
    logger.info("Testing concurrent model execution...")
    
    ai = AIModelIntegration()
    test_prompt = "Test prompt"
    test_data = {"test": "data"}
    
    # Make concurrent calls
    start = datetime.now()
    tasks = []
    for _ in range(5):
        tasks.extend([
            ai.get_claude_analysis(test_prompt, test_data),
            ai.get_gpt4_analysis(test_prompt, test_data),
            ai.get_mistral_analysis(test_prompt, test_data)
        ])
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    duration = (datetime.now() - start).total_seconds()
    
    # Check results
    successful = [r for r in results if not isinstance(r, Exception)]
    success_rate = len(successful) / len(results)
    
    assert success_rate >= 0.9, f"Concurrent execution success rate ({success_rate:.2%}) below threshold"
    assert duration < 15, f"Concurrent execution too slow ({duration:.2f}s)"
    
    logger.info("Concurrent calls: %d successful out of %d", len(successful), len(results))
    logger.info("Total duration: %.2fs", duration)
    logger.info("Concurrent execution test passed ✓")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
