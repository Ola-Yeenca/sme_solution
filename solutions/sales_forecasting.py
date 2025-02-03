"""Sales forecasting for businesses."""

import os
from typing import Dict, Any, List
import requests

from shared.business_data_fetcher import BusinessDataFetcher
from shared.ai_model_config import AIModel, ModelConfig

class SalesForecastingEngine:
    """Engine for sales forecasting and trend analysis."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher, business_type=None):
        """Initialize the sales forecasting engine with a data fetcher and optional business type."""
        self.data_fetcher = data_fetcher
        self.business_type = business_type
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for sales forecasting
        self.model = ModelConfig.get_recommended_model("sales_forecasting")
        self.model_config = ModelConfig.get_model_config(self.model)

    def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze sales forecast for a business."""
        try:
            # Get business details
            business_data = self.data_fetcher.get_business_details(business_name)
            
            # Get AI analysis using Claude-3
            analysis = self._get_ai_analysis(business_name, business_data)
            
            # Return just the analysis text
            return {
                'analysis_text': analysis
            }
            
        except Exception as e:
            raise Exception(f"Error in sales forecasting: {str(e)}")

    def _get_ai_analysis(self, business_name: str, business_data: Dict[str, Any]) -> str:
        """Get AI-powered sales forecast using Claude-3."""
        try:
            # Create detailed prompt
            prompt = f"""
            As a sales forecasting expert, provide a comprehensive forecast analysis for {business_name}:
            
            BUSINESS INFO:
            - Name: {business_name}
            - Rating: {business_data.get('rating', 0)}/5.0
            - Reviews: {business_data.get('reviews_count', 0)}
            - Price Level: {business_data.get('price_level', '€')}
            
            Please provide a detailed forecast analysis including:
            1. SALES TRENDS
            - Historical performance analysis based on ratings and reviews
            - Seasonal patterns for this type of business
            - Growth trajectory based on market conditions
            
            2. MARKET FACTORS
            - Economic indicators affecting the business
            - Industry trends in the region
            - Local market conditions and competition
            
            3. REVENUE PROJECTIONS
            - Short-term forecast (3-6 months)
            - Medium-term outlook (6-12 months)
            - Long-term potential (1-2 years)
            
            4. GROWTH OPPORTUNITIES
            - Market expansion potential
            - Revenue diversification strategies
            - Capacity optimization recommendations
            
            5. RISK FACTORS
            - Market uncertainties and challenges
            - Competitive threats in the area
            - External factors to monitor
            """
            
            # Make API request to OpenRouter
            response = requests.post(
                self.model_config["url"],
                headers={
                    **self.model_config["headers"],
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model_config["model"],
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
                
            response_data = response.json()
            
            # Extract just the analysis content from Claude's response
            return response_data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid API response format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in AI analysis: {str(e)}")

def run_sales_forecasting(business_name: str, tripadvisor_data: Dict[str, Any]):
    """Run sales forecasting analysis."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
    data_fetcher = BusinessDataFetcher(BusinessType.RESTAURANT)
    analyzer = SalesForecastingEngine(data_fetcher)
    return analyzer.analyze(business_name)