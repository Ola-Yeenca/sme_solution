"""Dynamic pricing analysis for businesses."""

import os
from typing import Dict, Any, List
import requests

from shared.business_data_fetcher import BusinessDataFetcher
from shared.ai_model_config import AIModel, ModelConfig

class DynamicPricingAnalyzer:
    """Analyzer for dynamic pricing recommendations."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher):
        """Initialize with a data fetcher."""
        self.data_fetcher = data_fetcher
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for pricing analysis
        self.model = ModelConfig.get_recommended_model("pricing_analysis")
        self.model_config = ModelConfig.get_model_config(self.model)

    def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze pricing for a business."""
        try:
            # Get business details and competitors
            business_data = self.data_fetcher.get_business_details(business_name)
            competitors = self.data_fetcher.get_competitors(business_name)
            
            # Get AI analysis using Claude-3
            analysis = self._get_ai_analysis(business_name, business_data, competitors)
            
            # Return just the analysis text
            return {
                'analysis_text': analysis
            }
            
        except Exception as e:
            raise Exception(f"Error in pricing analysis: {str(e)}")

    def _get_ai_analysis(self, business_name: str, business_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> str:
        """Get AI-powered pricing analysis using Claude-3."""
        try:
            # Format competitors info
            competitors_info = "\n".join(
                f"- {comp['name']}: Rating {comp['rating']}/5.0, "
                f"Price Level {comp['price_level']}, "
                f"Distance: {comp.get('distance_km', 0):.1f}km"
                for comp in competitors[:5]  # Top 5 competitors
            )
            
            # Create detailed prompt
            prompt = f"""
            As a pricing strategy expert, provide a comprehensive pricing analysis for {business_name}:
            
            BUSINESS INFO:
            - Name: {business_name}
            - Rating: {business_data.get('rating', 0)}/5.0
            - Price Level: {business_data.get('price_level', '€')}
            
            COMPETITORS:
            {competitors_info}
            
            Please provide a detailed pricing strategy including:
            1. MARKET POSITION
            - Current price positioning
            - Value perception analysis
            - Competitive advantage assessment
            
            2. PRICING RECOMMENDATIONS
            - Optimal price points
            - Seasonal adjustments
            - Special offers strategy
            
            3. REVENUE OPTIMIZATION
            - Demand patterns
            - Yield management
            - Capacity utilization
            
            4. COMPETITIVE STRATEGY
            - Price differentiation
            - Value-added services
            - Market segmentation
            
            5. IMPLEMENTATION PLAN
            - Pricing calendar
            - Monitoring metrics
            - Adjustment triggers
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

def run_dynamic_pricing(business_name: str, tripadvisor_data: Dict[str, Any]):
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return
    
    if not tripadvisor_data or tripadvisor_data.get('error'):
        print(f"\nNote: Using default values as TripAdvisor data is not available.")
        print(f"Error: {tripadvisor_data.get('error') if tripadvisor_data else 'No data available'}")
        current_price = 15.0
    else:
        current_price = 15.0  # Removed DynamicPricingEngine._estimate_price
    
    try:
        weather = get_weather_data()
        weather_summary = {
            "temperature": weather["main"]["temp"],
            "description": weather["weather"][0]["description"],
            "humidity": weather["main"]["humidity"],
            "feels_like": weather["main"]["feels_like"]
        }
    except Exception as e:
        print(f"Warning: Could not fetch weather data: {e}")
        weather_summary = {
            "temperature": 20,
            "description": "unknown",
            "humidity": 60,
            "feels_like": 20
        }
    
    try:
        events = get_event_data()
    except Exception as e:
        print(f"Warning: Could not fetch events data: {e}")
        events = []
    
    try:
        competitors = get_competitor_pricing(business_name)
    except Exception as e:
        print(f"Warning: Could not fetch competitor data: {e}")
        competitors = []
    
    sales_data = {
        "last_week": [100, 120, 140, 130, 150, 160, 140],
        "average_ticket": current_price,
        "peak_hours": ["13:00-15:00", "20:00-22:00"]
    }
    
    print("\n=== Business Optimization Analysis ===")
    print(f"Business: {business_name}")
    print(f"\nCurrent Price: €{current_price:.2f}")
    print(f"Number of Competitors Analyzed: {len(competitors)}")
    
    if len(competitors) > 0:
        avg_competitor_price = sum(c['price'] for c in competitors) / len(competitors)
        print(f"Average Competitor Price: €{avg_competitor_price:.2f}")
    
    analyzer = DynamicPricingAnalyzer(BusinessDataFetcher(business_name))
    analysis = analyzer.analyze(business_name)
    print("\nAnalysis:")
    print(analysis)
    print("\nNote: These suggestions are based on current market conditions and should be reviewed regularly.")