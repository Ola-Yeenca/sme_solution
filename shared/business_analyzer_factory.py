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
        import inspect
        import logging
        logger = logging.getLogger(__name__)
        try:
            analyzer_class = self.SUPPORTED_ANALYZERS.get(analysis_type)
            if not analyzer_class:
                raise ValueError(
                    f"Invalid analysis type. Must be one of: {', '.join(self.SUPPORTED_ANALYZERS.keys())}"
                )

            # Get __init__ parameters excluding self
            sig = inspect.signature(analyzer_class.__init__)
            params = list(sig.parameters.values())[1:]
            logger.debug(f"Analyzing {analyzer_class.__name__} parameters: {params}")
            
            # Check for any business_type parameters (including variants)
            business_type_params = [p for p in params if 'business_type' in p.name]
            logger.debug(f"Business type parameters found: {business_type_params}")
            
            if business_type_params:
                param = business_type_params[0]
                if param.default == inspect.Parameter.empty:
                    logger.info(f"Creating {analyzer_class.__name__} with required business_type")
                    return analyzer_class(self.data_fetcher, business_type)
                else:
                    logger.info(f"Creating {analyzer_class.__name__} with optional business_type")
                    return analyzer_class(self.data_fetcher, business_type)
            else:
                logger.info(f"Creating {analyzer_class.__name__} without business_type")
                return analyzer_class(self.data_fetcher)
        except Exception as e:
            logger.error(f"Error creating analyzer: {str(e)}")
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
