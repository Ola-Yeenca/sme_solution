"""Dynamic pricing analyzer for business data."""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from statistics import mean, median

from smeanalytica.shared.business_data_fetcher import BusinessDataFetcher
from smeanalytica.config.business_types import BusinessType
from smeanalytica.config.analysis_types import AnalysisType
from smeanalytica.config.ai_model_config import ModelConfig, AIModel

logger = logging.getLogger(__name__)

class DynamicPricingAnalyzer:
    """Analyzer for dynamic pricing recommendations."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher, business_type: Optional[str] = None):
        """Initialize the analyzer."""
        self.data_fetcher = data_fetcher
        self.business_type = business_type or BusinessType.RESTAURANT
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get recommended AI model for pricing analysis
        self.model = ModelConfig.get_recommended_model("pricing_analysis")
        
    async def analyze_pricing(self, business_name: str) -> Dict[str, Any]:
        """Analyze pricing for a business."""
        try:
            # Get business data
            business_data = await self.data_fetcher.get_business_data(business_name)
            if not business_data:
                raise ValueError(f"No data found for business: {business_name}")
                
            # Get competitor data
            competitors = await self.data_fetcher.get_competitors(business_name)
            
            # Analyze current pricing
            current_pricing = self._analyze_current_pricing(business_data)
            
            # Analyze competitor pricing
            competitor_pricing = self._analyze_competitor_pricing(competitors)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                current_pricing,
                competitor_pricing,
                business_data
            )
            
            return {
                'status': 'success',
                'current_pricing': current_pricing,
                'competitor_pricing': competitor_pricing,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pricing for {business_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def _analyze_current_pricing(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current pricing strategy."""
        try:
            price_level = business_data.get('price_level', 0)
            rating = business_data.get('rating', 0.0)
            reviews = business_data.get('reviews', [])
            
            # Calculate average sentiment from reviews
            sentiment_scores = [
                review.get('rating', 0)
                for review in reviews
                if review.get('rating') is not None
            ]
            avg_sentiment = mean(sentiment_scores) if sentiment_scores else 0
            
            return {
                'price_level': price_level,
                'rating': rating,
                'average_sentiment': avg_sentiment,
                'review_count': len(reviews),
                'price_perception': self._calculate_price_perception(
                    price_level,
                    rating,
                    avg_sentiment
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing current pricing: {str(e)}")
            return {}
            
    def _analyze_competitor_pricing(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitor pricing strategies."""
        try:
            if not competitors:
                return {'status': 'no_competitors'}
                
            price_levels = [
                comp.get('price_level', 0)
                for comp in competitors
                if comp.get('price_level') is not None
            ]
            
            ratings = [
                comp.get('rating', 0.0)
                for comp in competitors
                if comp.get('rating') is not None
            ]
            
            return {
                'average_price_level': mean(price_levels) if price_levels else 0,
                'median_price_level': median(price_levels) if price_levels else 0,
                'average_rating': mean(ratings) if ratings else 0.0,
                'competitor_count': len(competitors),
                'price_distribution': self._calculate_price_distribution(price_levels)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitor pricing: {str(e)}")
            return {}
            
    def _generate_recommendations(
        self,
        current_pricing: Dict[str, Any],
        competitor_pricing: Dict[str, Any],
        business_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate pricing recommendations."""
        try:
            current_price_level = current_pricing.get('price_level', 0)
            avg_competitor_price = competitor_pricing.get('average_price_level', 0)
            
            # Calculate optimal price level
            if current_price_level > avg_competitor_price:
                if current_pricing.get('rating', 0) > competitor_pricing.get('average_rating', 0):
                    recommendation = "maintain_premium"
                else:
                    recommendation = "adjust_downward"
            else:
                if current_pricing.get('price_perception', 0) > 0.7:
                    recommendation = "increase_gradually"
                else:
                    recommendation = "maintain_competitive"
                    
            return {
                'recommendation': recommendation,
                'confidence': self._calculate_confidence(
                    current_pricing,
                    competitor_pricing
                ),
                'suggested_actions': self._get_suggested_actions(recommendation),
                'market_position': self._analyze_market_position(
                    current_pricing,
                    competitor_pricing
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {}
            
    def _calculate_price_perception(
        self,
        price_level: int,
        rating: float,
        sentiment: float
    ) -> float:
        """Calculate price perception score."""
        try:
            # Normalize inputs
            norm_price = price_level / 4.0  # Assuming max price_level is 4
            norm_rating = rating / 5.0
            norm_sentiment = sentiment / 5.0
            
            # Weight factors
            price_weight = 0.4
            rating_weight = 0.35
            sentiment_weight = 0.25
            
            # Calculate weighted score
            perception = (
                (1 - norm_price) * price_weight +
                norm_rating * rating_weight +
                norm_sentiment * sentiment_weight
            )
            
            return round(perception, 2)
            
        except Exception as e:
            logger.error(f"Error calculating price perception: {str(e)}")
            return 0.0
            
    def _calculate_price_distribution(self, price_levels: List[int]) -> Dict[str, int]:
        """Calculate distribution of competitor price levels."""
        try:
            distribution = {
                'budget': 0,
                'moderate': 0,
                'expensive': 0,
                'luxury': 0
            }
            
            for price in price_levels:
                if price <= 1:
                    distribution['budget'] += 1
                elif price == 2:
                    distribution['moderate'] += 1
                elif price == 3:
                    distribution['expensive'] += 1
                else:
                    distribution['luxury'] += 1
                    
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating price distribution: {str(e)}")
            return {}
            
    def _calculate_confidence(
        self,
        current_pricing: Dict[str, Any],
        competitor_pricing: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for recommendations."""
        try:
            factors = [
                current_pricing.get('review_count', 0) >= 10,
                competitor_pricing.get('competitor_count', 0) >= 5,
                current_pricing.get('rating', 0) > 0,
                competitor_pricing.get('average_rating', 0) > 0
            ]
            
            confidence = sum(1 for f in factors if f) / len(factors)
            return round(confidence, 2)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0
            
    def _get_suggested_actions(self, recommendation: str) -> List[str]:
        """Get suggested actions based on recommendation."""
        actions = {
            'maintain_premium': [
                'Focus on maintaining high service quality',
                'Highlight unique value propositions',
                'Consider loyalty programs for regular customers'
            ],
            'adjust_downward': [
                'Gradually reduce prices on selected items',
                'Introduce value meals or combos',
                'Implement happy hour or special promotions'
            ],
            'increase_gradually': [
                'Slowly increase prices on premium items',
                'Add premium options to the menu',
                'Enhance presentation and service quality'
            ],
            'maintain_competitive': [
                'Monitor competitor pricing regularly',
                'Focus on cost optimization',
                'Consider seasonal promotions'
            ]
        }
        return actions.get(recommendation, ['Review pricing strategy'])

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