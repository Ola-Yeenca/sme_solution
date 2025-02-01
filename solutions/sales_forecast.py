"""Sales forecasting for businesses."""

import os
from typing import Dict, Any, List
import requests
from datetime import datetime, timedelta

from shared.business_data_fetcher import BusinessDataFetcher
from shared.ai_model_config import AIModel, ModelConfig

class SalesForecastAnalyzer:
    """Analyzer for sales forecasting and growth predictions."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher):
        """Initialize with a data fetcher."""
        self.data_fetcher = data_fetcher
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for sales forecasting
        self.model = ModelConfig.get_recommended_model("sales_forecast")
        self.model_config = ModelConfig.get_model_config(self.model)

    def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze and forecast sales for a business."""
        try:
            # Get comprehensive business details
            business_data = self.data_fetcher.get_business_details(business_name)
            
            # Get historical data for trend analysis
            historical_data = self.data_fetcher.get_historical_data(business_name)
            
            # Get competitors for market context
            competitors = self.data_fetcher.get_competitors(business_name)
            
            # Get AI analysis
            analysis = self._get_ai_analysis(business_name, business_data, historical_data, competitors)
            
            return {
                'business_metrics': {
                    'current_performance': {
                        'rating': business_data.get('rating', 0),
                        'reviews_count': business_data.get('reviews_count', 0),
                        'price_level': business_data.get('price_level', '€€'),
                        'market_share': business_data.get('local_market_share', 0)
                    },
                    'historical_trends': historical_data,
                    'market_position': business_data.get('market_position', {})
                },
                'forecast_analysis': analysis
            }
            
        except Exception as e:
            raise Exception(f"Error in sales forecasting: {str(e)}")

    def _get_ai_analysis(self, business_name: str, business_data: Dict[str, Any], 
                        historical_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> str:
        """Get AI-powered sales forecast analysis."""
        try:
            # Format historical performance data
            historical_summary = self._format_historical_data(historical_data)
            
            # Format competitor information
            competitors_info = self._format_competitor_data(competitors)
            
            # Create prompt for AI analysis
            prompt = f"""As an expert business analyst, provide a comprehensive sales forecast and growth analysis for {business_name}. 
            
Business Profile:
- Current Rating: {business_data.get('rating', 'N/A')}/5.0
- Price Level: {business_data.get('price_level', 'N/A')}
- Market Share: {business_data.get('local_market_share', 0)*100:.1f}%
- Cuisine Type: {', '.join(business_data.get('cuisine', []))}

Historical Performance:
{historical_summary}

Competitive Landscape:
{competitors_info}

Please provide a detailed analysis including:
1. Sales Growth Forecast
   - Short-term (3 months)
   - Medium-term (6-12 months)
   - Long-term (2-3 years)

2. Market Opportunities
   - Untapped customer segments
   - Service expansion possibilities
   - Peak season optimization

3. Revenue Optimization Strategies
   - Pricing optimization
   - Capacity utilization
   - Customer retention

4. Risk Assessment
   - Market risks
   - Competitive threats
   - Economic factors

5. Action Plan
   - Immediate steps
   - Resource requirements
   - Implementation timeline

Focus on practical, actionable recommendations that will drive sustainable growth while maintaining profitability."""

            # Get AI analysis
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.model_config['endpoint'],
                headers=headers,
                json={
                    "model": self.model_config['model_id'],
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.text}")
                
            analysis = response.json()['choices'][0]['message']['content']
            return analysis
            
        except Exception as e:
            raise Exception(f"Error in AI analysis: {str(e)}")

    def _format_historical_data(self, historical_data: Dict[str, Any]) -> str:
        """Format historical data for AI analysis."""
        if not historical_data:
            return "No historical data available."
            
        summary = []
        for period, metrics in historical_data.items():
            summary.append(f"Period: {period}")
            for metric, value in metrics.items():
                summary.append(f"- {metric}: {value}")
        
        return "\n".join(summary)

    def _format_competitor_data(self, competitors: List[Dict[str, Any]]) -> str:
        """Format competitor data for AI analysis."""
        if not competitors:
            return "No competitor data available."
            
        summary = []
        for comp in competitors[:5]:  # Top 5 competitors
            summary.append(
                f"- {comp['name']}: Rating {comp['rating']}/5.0, "
                f"Price Level {comp['price_level']}, "
                f"Distance: {comp.get('distance_km', 0):.1f}km"
            )
        
        return "\n".join(summary)
