"""Sales forecasting for businesses."""

import os
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import statistics

from smeanalytica.shared.business_data_fetcher import BusinessDataFetcher
from smeanalytica.shared.cache import DataCache
from smeanalytica.utils.performance import PerformanceMonitor
from smeanalytica.solutions.simple_forecast import SimpleForecastAnalyzer

logger = logging.getLogger(__name__)
performance = PerformanceMonitor()

class SalesForecastAnalyzer:
    """Analyzer for sales forecasting and growth predictions."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher, cache: DataCache):
        """Initialize with a data fetcher."""
        self.data_fetcher = data_fetcher
        self.cache = cache
        self.business_type = data_fetcher.business_type
        self.simple_forecast = SimpleForecastAnalyzer(self.business_type)

    async def initialize(self):
        await self.cache.initialize()

    async def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze and forecast sales for a business."""
        await self.cache.initialize()
        cache_key = f"sales_forecast:{business_name}:{self.business_type.value.upper()}"
        logger.debug(f"Checking cache for key: {cache_key}")
        result = await self.cache.get(cache_key)
        if result:
            return result
        
        try:
            with performance.measure(f"forecast_analysis_{business_name}"):
                logger.info(f"Starting sales forecast analysis for {business_name}")
                
                # Get comprehensive business details
                business_data = await self.data_fetcher.get_business_details(business_name)
                if not business_data:
                    raise ValueError(f"No data found for business: {business_name}")
                
                # Get historical data for trend analysis
                historical_data = await self.data_fetcher.get_historical_data(business_name)
                if not historical_data:
                    raise ValueError(f"No historical data available for: {business_name}")
                
                # Get competitors for market context
                competitors = await self.data_fetcher.get_competitors(business_name)
                
                # Generate forecast using simple statistical methods
                forecast_results = self.simple_forecast.forecast(historical_data)
                
                # Prepare market context
                market_context = self._analyze_market_context(business_data, competitors)
                
                forecast_values = forecast_results['forecast_values']
                current_performance = {
                    'rating': business_data.get('rating', 0),
                    'reviews_count': business_data.get('reviews_count', 0),
                    'price_level': business_data.get('price_level', '€€'),
                    'market_share': business_data.get('local_market_share', 0)
                }
                growth_potential = {
                    'historical_trends': historical_data,
                    'market_position': market_context
                }
                business_metrics = {
                    'current_performance': current_performance,
                    'growth_potential': growth_potential
                }
                
                recommendations = self._generate_recommendations(
                    forecast_results,
                    market_context,
                    business_data
                )
                
                # Store final result in cache
                result = {
                    'forecast_values': forecast_values,
                    'business_metrics': {
                        'current_performance': business_data,
                        'historical_trends': historical_data,
                        'market_context': {
                            'competitors': competitors,
                            'market_share': market_context['market_share'],
                            'total_market_size': market_context['total_market_size'],
                            'competitive_position': market_context['competitive_position']
                        }
                    }
                }
                
                logger.info(f"Storing forecast result in cache: {cache_key}")
                await self.cache.set(cache_key, result)
                return result
            
        except Exception as e:
            logger.error(f"Error in sales forecasting: {str(e)}")
            raise

    def _analyze_market_context(self, business_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market context using business data and competitors."""
        total_reviews = business_data.get('reviews_count', 0)
        total_reviews += sum(comp.get('reviews_count', 0) for comp in competitors)
        
        # Calculate market share based on review count
        market_share = (business_data.get('reviews_count', 0) / total_reviews) if total_reviews > 0 else 0
        
        # Analyze competitive position
        avg_competitor_rating = statistics.mean([comp.get('rating', 0) for comp in competitors]) if competitors else 0
        rating_position = business_data.get('rating', 0) - avg_competitor_rating
        
        return {
            'market_share': market_share,
            'total_market_size': total_reviews,
            'competitive_position': {
                'rating_difference': rating_position,
                'num_competitors': len(competitors)
            }
        }

    def _generate_recommendations(
        self,
        forecast_results: Dict[str, Any],
        market_context: Dict[str, Any],
        business_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Trend-based recommendations
        trend = forecast_results['trend_analysis']
        if trend['direction'] == 'decreasing':
            recommendations.append({
                'category': 'growth',
                'priority': 'high',
                'suggestion': 'Consider promotional activities to reverse negative trend',
                'reasoning': 'Sales showing downward trend with strength ' + str(trend['strength'])
            })
        
        # Seasonal recommendations
        seasonal = forecast_results['seasonal_patterns']
        if seasonal['peak_months']:
            recommendations.append({
                'category': 'seasonal',
                'priority': 'medium',
                'suggestion': f"Prepare for peak seasons in months: {', '.join(map(str, seasonal['peak_months']))}",
                'reasoning': 'Historical data shows increased activity during these months'
            })
        
        # Competition-based recommendations
        if market_context['competitive_position']['rating_difference'] < 0:
            recommendations.append({
                'category': 'service',
                'priority': 'high',
                'suggestion': 'Focus on service quality improvement',
                'reasoning': 'Rating is below market average'
            })
        
        return recommendations
