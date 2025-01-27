"""Factory for creating business analyzers based on business type."""

from typing import Optional, Dict, Any
from config.business_types import BusinessType

from shared.business_data_fetcher import BusinessDataFetcher
from solutions.dynamic_pricing import DynamicPricingAnalyzer
from solutions.sentiment_analysis import SentimentAnalyzer
from solutions.competitor_analysis import CompetitorAnalyzer
from solutions.sales_forecasting import SalesForecastingEngine

class BusinessAnalyzerFactory:
    """Factory class for creating business analyzers."""
    
    SUPPORTED_ANALYZERS = {
        'pricing': DynamicPricingAnalyzer,
        'sentiment': SentimentAnalyzer,
        'competitors': CompetitorAnalyzer,
        'forecast': SalesForecastingEngine
    }

    def __init__(self, data_fetcher: BusinessDataFetcher):
        """Initialize with a data fetcher."""
        if not isinstance(data_fetcher, BusinessDataFetcher):
            raise ValueError("data_fetcher must be an instance of BusinessDataFetcher")
        self.data_fetcher = data_fetcher

    def create_analyzer(self, business_type: str, analysis_type: str) -> Optional[Any]:
        """Create an analyzer based on analysis type."""
        try:
            analyzer_class = self.SUPPORTED_ANALYZERS.get(analysis_type)
            if not analyzer_class:
                raise ValueError(
                    f"Invalid analysis type. Must be one of: {', '.join(self.SUPPORTED_ANALYZERS.keys())}"
                )
                
            return analyzer_class(self.data_fetcher)
            
        except Exception as e:
            raise Exception(f"Error creating analyzer: {str(e)}")

    @classmethod
    def get_supported_analyzers(cls) -> Dict[str, str]:
        """Get a list of supported analyzer types and their descriptions."""
        return {
            'pricing': 'Dynamic pricing analysis and optimization',
            'sentiment': 'Customer sentiment and feedback analysis',
            'competitors': 'Competitor analysis and market positioning',
            'forecast': 'Sales forecasting and trend analysis'
        }
