"""Analysis types and configurations."""

from enum import Enum
from typing import Dict, Any

class AnalysisType(Enum):
    """Types of analysis available in the system."""
    
    DYNAMIC_PRICING = "dynamic_pricing"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SALES_FORECASTING = "sales_forecasting"
    
    @staticmethod
    def get_model_config(analysis_type: 'AnalysisType') -> Dict[str, Any]:
        """Get the model configuration for a specific analysis type."""
        configs = {
            AnalysisType.DYNAMIC_PRICING: {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 1.0
            },
            AnalysisType.SENTIMENT_ANALYSIS: {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.5,
                "max_tokens": 1500,
                "top_p": 1.0
            },
            AnalysisType.COMPETITOR_ANALYSIS: {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 1.0
            },
            AnalysisType.SALES_FORECASTING: {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.3,
                "max_tokens": 1000,
                "top_p": 1.0
            }
        }
        return configs.get(analysis_type, {})
