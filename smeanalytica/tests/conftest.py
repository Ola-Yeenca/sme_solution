"""Test configuration and fixtures for SME Analytica."""

import os
import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from smeanalytica.core.analyzers.business_analyzer import BusinessAnalyzer
from smeanalytica.core.models.model_manager import ModelManager
from smeanalytica.core.data.data_source_manager import DataSourceManager
from smeanalytica.core.models.feature_engineering import FeatureEngineering

@pytest.fixture
def test_data_path() -> Path:
    """Get path to test data directory."""
    return Path(__file__).parent / 'data'

@pytest.fixture
def sample_reviews(test_data_path) -> pd.DataFrame:
    """Load sample review data."""
    return pd.read_csv(test_data_path / 'sample_reviews.csv')

@pytest.fixture
def historical_sales(test_data_path) -> pd.DataFrame:
    """Load historical sales data."""
    return pd.read_csv(test_data_path / 'historical_sales.csv')

@pytest.fixture
def competitor_data(test_data_path) -> pd.DataFrame:
    """Load competitor data."""
    return pd.read_csv(test_data_path / 'competitor_data.csv')

@pytest.fixture
def model_manager() -> ModelManager:
    """Create ModelManager instance."""
    return ModelManager()

@pytest.fixture
def data_manager() -> DataSourceManager:
    """Create DataSourceManager instance."""
    return DataSourceManager()

@pytest.fixture
def feature_engineering() -> FeatureEngineering:
    """Create FeatureEngineering instance."""
    return FeatureEngineering()

@pytest.fixture
def business_analyzer(model_manager) -> BusinessAnalyzer:
    """Create BusinessAnalyzer instance."""
    return BusinessAnalyzer(model_manager.get_model('sentiment_analysis'))

@pytest.fixture
def sample_businesses() -> list:
    """List of real businesses for testing."""
    return [
        "The French Laundry",
        "Alinea",
        "Le Bernardin",
        "Eleven Madison Park",
        "Per Se"
    ]

@pytest.fixture
def expected_response_schema() -> Dict[str, Any]:
    """Expected schema for analysis responses."""
    return {
        "business": str,
        "analysis_type": str,
        "result": dict,
        "confidence": float,
        "timestamp": str
    }

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Backup original values
    original_env = {
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY'),
        'GOOGLE_PLACES_API_KEY': os.environ.get('GOOGLE_PLACES_API_KEY'),
        'YELP_API_KEY': os.environ.get('YELP_API_KEY')
    }
    
    # Set test values
    os.environ['TESTING'] = 'true'
    os.environ['OPENROUTER_API_KEY'] = 'test_openrouter_key'
    os.environ['GOOGLE_PLACES_API_KEY'] = 'test_google_places_key'
    os.environ['YELP_API_KEY'] = 'test_yelp_key'
    
    yield
    
    # Restore original values
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]
    
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
