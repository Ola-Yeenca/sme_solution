"""Business analysis functionality for the SME Analytica application."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
import xgboost as xgb
import numpy as np
import pandas as pd
from textblob import TextBlob

from .base_analyzer import BaseAnalyzer, AnalysisResult, MarketData, Recommendation, AnalysisData
from ..data.data_source_manager import DataSourceManager
from ..models.ai_integrations import AIModelIntegration
from ..models.feature_engineering import FeatureEngineering
from ..data.data_source_manager import DataSourceManager

logger = logging.getLogger(__name__)

class BusinessAnalyzer(BaseAnalyzer):
    """Core business analysis functionality."""
    
    def __init__(self, model: Dict[str, Any], business_type: Optional[str] = None):
        """Initialize the analyzer with model configuration and business type."""
        super().__init__(model, business_type)
        self.data_manager = DataSourceManager()
        self.ai_integration = AIModelIntegration()
        self.feature_engineering = FeatureEngineering()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze business data based on the specified type.
        
        Args:
            data: Dictionary containing business data including:
                - business_name: Name of the business
                - business_type: Type of business
                - location: Location of the business
                - analysis_type: Type of analysis to perform
                
        Returns:
            AnalysisResult containing analysis data and recommendations
        """
        try:
            # Extract required fields
            business_name = data.get('business_name')
            business_type = data.get('business_type')
            location = data.get('location')
            analysis_type = data.get('analysis_type', 'dynamic_pricing')

            if not all([business_name, business_type, location]):
                return self._create_error_result("Missing required fields: business_name, business_type, or location")

            # Get business data
            try:
                business_data = await self.data_manager.get_business_data(
                    business_name=business_name,
                    business_type=business_type,
                    location=location
                )
                
                # Merge request data with business data
                analysis_data = {
                    **business_data,
                    'business_name': business_name,
                    'business_type': business_type,
                    'location': location,
                    'analysis_type': analysis_type
                }
                
            except Exception as e:
                logger.error(f"Failed to get business data: {str(e)}", exc_info=True)
                return self._create_error_result(f"Failed to get business data: {str(e)}")
            
            # Process data based on analysis type
            try:
                if analysis_type == 'sentiment':
                    result = await self._analyze_sentiment(analysis_data)
                elif analysis_type == 'dynamic_pricing':
                    result = await self._analyze_dynamic_pricing(analysis_data)
                elif analysis_type == 'pricing':
                    result = await self._analyze_basic_pricing(analysis_data)
                elif analysis_type == 'competition':
                    result = await self._analyze_competitors(analysis_data)
                elif analysis_type == 'market':
                    result = await self._analyze_market(analysis_data)
                else:
                    return self._create_error_result(f"Unsupported analysis type: {analysis_type}")

                return result
                
            except Exception as e:
                logger.error(f"Analysis processing failed: {str(e)}", exc_info=True)
                return self._create_error_result(f"Analysis processing failed: {str(e)}")
                
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._create_error_result(f"Analysis failed: {str(e)}")

    async def _analyze_sentiment(self, data: Dict[str, Any]) -> AnalysisResult:
        """Analyze sentiment from reviews and customer feedback."""
        try:
            # Get reviews from data manager
            reviews = await self.data_manager.get_reviews(
                business_name=data.get('business_name')
            )
            
            # Check if we only have the default review
            if len(reviews) == 1 and reviews[0].get('source') == 'default':
                return AnalysisResult(
                    success=True,
                    data={
                        'sentiment_analysis': {
                            'overall_sentiment': 'neutral',
                            'sentiment_scores': {
                                'positive': 0.0,
                                'neutral': 1.0,
                                'negative': 0.0
                            },
                            'key_findings': [
                                "No reviews available for sentiment analysis",
                                "Unable to determine customer sentiment at this time",
                                "Consider encouraging customers to leave reviews",
                                "This is a placeholder analysis"
                            ],
                            'review_highlights': {
                                'positive': [],
                                'negative': []
                            },
                            'sentiment_trends': [
                                {
                                    'trend': 'Review Collection Needed',
                                    'score': 0.5
                                }
                            ]
                        }
                    }
                )
            
            # Process reviews with TextBlob
            sentiments = [TextBlob(review.get('text', '')).sentiment.polarity for review in reviews]
            
            # Calculate sentiment scores
            total = len(sentiments)
            if total == 0:
                return self._create_error_result("No reviews found for sentiment analysis")
                
            positive = sum(1 for s in sentiments if s > 0.1)
            negative = sum(1 for s in sentiments if s < -0.1)
            neutral = total - positive - negative
            
            positive_score = positive / total
            negative_score = negative / total
            neutral_score = neutral / total
            
            # Determine overall sentiment
            overall_sentiment = 'positive' if positive_score > 0.5 else 'negative' if negative_score > 0.5 else 'neutral'
            
            # Process review texts for highlights
            positive_reviews = [r['text'] for r in reviews if TextBlob(r.get('text', '')).sentiment.polarity > 0.1][:3]
            negative_reviews = [r['text'] for r in reviews if TextBlob(r.get('text', '')).sentiment.polarity < -0.1][:3]
            
            # Calculate sentiment trends
            current_year = datetime.now().year
            # Handle both string dates and integer timestamps
            recent_reviews = []
            for r in reviews:
                time_created = r.get('time_created', '')
                if isinstance(time_created, int):
                    # Convert timestamp to year
                    review_year = datetime.fromtimestamp(time_created).year
                elif isinstance(time_created, str):
                    # Try to extract year from string date
                    try:
                        review_year = int(time_created[:4])
                    except (ValueError, IndexError):
                        review_year = 0
                else:
                    review_year = 0
                
                if review_year == current_year:
                    recent_reviews.append(r)
            
            if recent_reviews:
                recent_sentiments = [TextBlob(r.get('text', '')).sentiment.polarity for r in recent_reviews]
                recent_positive = sum(1 for s in recent_sentiments if s > 0.1) / len(recent_sentiments)
            else:
                recent_positive = positive_score
            
            # Create sentiment analysis data structure that matches frontend expectations
            sentiment_data = {
                'sentiment_analysis': {
                    'overall_sentiment': overall_sentiment,
                    'sentiment_scores': {
                        'positive': positive_score,
                        'neutral': neutral_score,
                        'negative': negative_score
                    },
                    'key_findings': [
                        f"Overall sentiment is {overall_sentiment}",
                        f"{(positive_score * 100):.1f}% of reviews are positive",
                        f"{(negative_score * 100):.1f}% of reviews are negative",
                        f"Based on {total} reviews analyzed"
                    ],
                    'review_highlights': {
                        'positive': positive_reviews,
                        'negative': negative_reviews
                    },
                    'sentiment_trends': [
                        {
                            'trend': 'Recent Reviews',
                            'score': recent_positive
                        },
                        {
                            'trend': 'Overall Sentiment',
                            'score': (positive_score * 1.0 + neutral_score * 0.5)
                        }
                    ]
                }
            }
            
            return AnalysisResult(
                success=True,
                data=sentiment_data
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}", exc_info=True)
            return self._create_error_result(f"Sentiment analysis failed: {str(e)}")
    
    async def _analyze_basic_pricing(self, data: Dict[str, Any]) -> AnalysisResult:
        """Analyze basic pricing strategy using cost-based approach."""
        try:
            # Get base data
            costs = data.get('costs', {})
            market_data = await self.data_manager._get_market_data(
                data.get('business_type', ''),
                data.get('location', '')
            )
            
            # Get competitor data for market context
            competitors = data.get('competitors', [])
            avg_competitor_price = 2.0  # default mid-range
            if competitors:
                valid_prices = [c.get('price_level', 2) for c in competitors if c.get('price_level') is not None]
                if valid_prices:
                    avg_competitor_price = sum(valid_prices) / len(valid_prices)

            # Calculate base price range using cost-plus pricing
            base_cost = costs.get('unit_cost', 10)  # default base cost if not provided
            min_markup = 1.3  # minimum 30% markup
            max_markup = 2.5  # maximum 150% markup
            
            min_price = round(base_cost * min_markup, 2)
            max_price = round(base_cost * max_markup, 2)

            # Simple market adjustment
            growth_rate = market_data.get('growth_rate', 0.04)
            market_adjustment = 1 + (growth_rate * 2)  # higher growth rate allows higher prices
            
            # Calculate recommended price and round to 2 decimal places
            recommended_price = round((min_price + max_price) / 2 * market_adjustment, 2)

            # Generate pricing factors
            factors = [
                f"Base cost: €{base_cost:.2f}",
                f"Market growth rate: {growth_rate * 100:.1f}%",
                f"Average competitor price level: {avg_competitor_price:.1f}",
                "Standard industry margins"
            ]

            # Generate basic recommendations
            recommendations = [
                f"Set base price at €{recommended_price:.2f}",
                f"Maintain price range between €{min_price:.2f} - €{max_price:.2f}",
                "Review pricing quarterly",
                "Monitor competitor price changes"
            ]

            return AnalysisResult(
                success=True,
                data={
                    'pricing': {
                        'recommended_base_price': float(recommended_price),
                        'min_price': float(min_price),
                        'max_price': float(max_price),
                        'factors': factors,
                        'recommendations': recommendations
                    }
                }
            )

        except Exception as e:
            logger.error(f"Basic pricing analysis failed: {str(e)}")
            return self._create_error_result(str(e))

    async def _analyze_dynamic_pricing(self, data: Dict[str, Any]) -> AnalysisResult:
        """Analyze dynamic pricing strategy using AI-driven approach."""
        try:
            # Get competitors from data
            competitors = data.get('competitors', [])
            if not competitors:
                return self._create_error_result("No competitor data available for analysis")
            
            business_name = data.get('business_name', '')
            business_type = data.get('business_type', '')
            
            # Calculate detailed competitor metrics
            competitor_metrics = []
            valid_competitors = 0
            total_rating = 0
            total_price = 0
            
            # Process competitor data
            for comp in competitors:
                rating = comp.get('rating')
                price_level = comp.get('price_level')
                
                if rating is None or price_level is None:
                    continue
                
                review_count = comp.get('reviews_count', 0)
                distance = comp.get('distance', 0)
                
                competitor_metrics.append({
                    'name': comp.get('name', ''),
                    'rating': rating,
                    'price_level': price_level,
                    'review_count': review_count,
                    'distance': distance,
                    'is_target': comp.get('is_target', False)
                })
                
                if not comp.get('is_target', False):
                    valid_competitors += 1
                    total_rating += rating
                    total_price += price_level
            
            if valid_competitors == 0:
                return self._create_error_result("No valid competitor data for analysis")
            
            # Calculate weighted averages
            avg_rating = total_rating / valid_competitors
            avg_price = total_price / valid_competitors
            
            # Get target business metrics
            target_business = next((comp for comp in competitor_metrics if comp.get('is_target', False)), None)
            business_rating = target_business['rating'] if target_business else data.get('rating', 0)
            business_price = target_business['price_level'] if target_business else data.get('price_level', 2)
            
            # Calculate dynamic price adjustments
            rating_diff = business_rating - avg_rating
            price_diff = business_price - avg_price
            
            # Determine market position
            if business_rating > avg_rating + 0.5:
                position = 'premium'
                confidence = 0.85
            elif business_rating < avg_rating - 0.5:
                position = 'budget'
                confidence = 0.75
            else:
                position = 'competitive'
                confidence = 0.8
            
            # Calculate base price range
            base_price = business_price * 10
            min_price = round(base_price * 0.8, 2)
            max_price = round(base_price * 1.4, 2)
            
            # Adjust based on market position
            if position == 'premium':
                recommended_price = round(base_price * (1.2 + rating_diff * 0.1), 2)
                strategy = "premium_dynamic"
            elif position == 'budget':
                recommended_price = round(base_price * (0.9 + rating_diff * 0.05), 2)
                strategy = "competitive_dynamic"
            else:
                recommended_price = round(base_price * (1.0 + rating_diff * 0.08), 2)
                strategy = "balanced_dynamic"
            
            # Generate dynamic pricing factors
            factors = [
                f"Market position: {position}",
                f"Rating differential: {rating_diff:+.2f}",
                f"Price level differential: {price_diff:+.2f}",
                f"Confidence level: {confidence:.0%}"
            ]
            
            # Generate dynamic recommendations
            recommendations = [
                f"Implement {strategy} pricing at €{recommended_price:.2f}",
                f"Adjust dynamically between €{min_price:.2f} - €{max_price:.2f}",
                self._get_dynamic_pricing_action(position, business_type),
                self._get_seasonal_recommendation(business_type)
            ]

            # Create market data
            market_data = {
                'average_competitor_rating': round(avg_rating, 2),
                'market_position': position,
                'average_competitor_price_level': round(avg_price, 2)
            }

            # Create recommendation data
            recommendation_data = {
                'pricing_strategy': strategy,
                'confidence': confidence,
                'explanation': f"Based on your {position} market position with a rating differential of {rating_diff:+.2f} and price differential of {price_diff:+.2f}",
                'suggested_actions': recommendations
            }

            return AnalysisResult(
                success=True,
                data={
                    'market_data': market_data,
                    'recommendation': recommendation_data
                }
            )

        except Exception as e:
            logger.error(f"Dynamic pricing analysis failed: {str(e)}", exc_info=True)
            return self._create_error_result(f"Dynamic pricing analysis failed: {str(e)}")

    def _get_dynamic_pricing_action(self, position: str, business_type: str) -> str:
        """Get dynamic pricing action based on market position."""
        actions = {
            'premium': {
                'restaurant': "Implement surge pricing during peak hours and events",
                'cafe': "Dynamic pricing for specialty items and peak times",
                'retail': "Premium pricing with dynamic seasonal adjustments",
                'fitness': "Dynamic membership tiers with peak/off-peak rates",
                'salon': "Premium service packages with dynamic pricing",
                'hotel': "Dynamic rates based on occupancy and events",
                'service': "Premium service tiers with dynamic pricing",
                'e-commerce': "Dynamic pricing based on demand and inventory"
            },
            'competitive': {
                'restaurant': "Balanced pricing with happy hour specials",
                'cafe': "Dynamic pricing for different dayparts",
                'retail': "Competitive pricing with dynamic promotions",
                'fitness': "Flexible membership options with dynamic rates",
                'salon': "Dynamic pricing for off-peak hours",
                'hotel': "Dynamic rates based on market demand",
                'service': "Dynamic pricing based on service demand",
                'e-commerce': "Dynamic pricing based on competition"
            },
            'budget': {
                'restaurant': "Volume-based dynamic pricing strategy",
                'cafe': "Dynamic value menu pricing",
                'retail': "Dynamic discount strategy",
                'fitness': "Dynamic pricing for class packages",
                'salon': "Dynamic pricing for service bundles",
                'hotel': "Dynamic rates for extended stays",
                'service': "Dynamic pricing for service packages",
                'e-commerce': "Dynamic pricing for bulk purchases"
            }
        }
        
        return actions.get(position, {}).get(
            business_type.lower(),
            f"Implement {position} dynamic pricing strategy"
        )

    def _calculate_competitor_metrics(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Calculate detailed competitor metrics with weighted averages."""
        valid_competitors = [c for c in competitors if not c.get('is_target', False)]
        if not valid_competitors:
            return None
            
        total_weight = 0
        weighted_ratings = []
        weighted_prices = []
        
        for comp in valid_competitors:
            # Calculate weight based on review count and distance
            review_count = comp.get('review_count', 0)
            distance = comp.get('distance', 0)
            
            review_weight = min(review_count / 100, 1.0) if review_count > 0 else 0.1
            distance_weight = 1 / (1 + distance / 1000) if distance > 0 else 1.0
            weight = review_weight * distance_weight
            
            rating = comp.get('rating', 0)
            price = comp.get('price_level', 2)
            
            total_weight += weight
            weighted_ratings.append(rating * weight)
            weighted_prices.append(price * weight)
        
        return {
            'avg_rating': sum(weighted_ratings) / total_weight,
            'avg_price': sum(weighted_prices) / total_weight,
            'total_competitors': len(valid_competitors),
            'price_distribution': self._calculate_price_distribution(valid_competitors)
        }

    def _calculate_price_distribution(self, competitors: List[Dict]) -> Dict[str, float]:
        """Calculate the distribution of competitor prices."""
        total = len(competitors)
        if total == 0:
            return {'budget': 0, 'mid': 0, 'premium': 0}
            
        price_levels = [c.get('price_level', 2) for c in competitors]
        return {
            'budget': len([p for p in price_levels if p < 2]) / total,
            'mid': len([p for p in price_levels if 2 <= p <= 3]) / total,
            'premium': len([p for p in price_levels if p > 3]) / total
        }

    def _get_target_business_metrics(self, data: Dict[str, Any], competitor_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get target business metrics with market context."""
        return {
            'rating': data.get('rating', 0),
            'price_level': data.get('price_level', 2),
            'review_count': data.get('review_count', 0),
            'relative_rating': data.get('rating', 0) - competitor_metrics['avg_rating'],
            'relative_price': data.get('price_level', 2) - competitor_metrics['avg_price']
        }

    def _determine_market_position(self, target_metrics: Dict[str, Any], competitor_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Determine detailed market position."""
        rating_diff = target_metrics['relative_rating']
        price_diff = target_metrics['relative_price']
        
        if rating_diff > 0.3:
            status = 'premium' if price_diff > 0 else 'value_leader'
        elif rating_diff < -0.3:
            status = 'overpriced' if price_diff > 0 else 'budget'
        else:
            status = 'competitive'
            
        return {
            'status': status,
            'rating_strength': rating_diff,
            'price_position': price_diff,
            'market_share': competitor_metrics['price_distribution']
        }

    def _calculate_dynamic_price_adjustments(self, target_metrics: Dict[str, Any], 
                                          competitor_metrics: Dict[str, Any],
                                          market_position: Dict[str, Any],
                                          business_type: str) -> Dict[str, Any]:
        """Calculate AI-driven dynamic price adjustments."""
        # Calculate competitive strength
        competitive_strength = (
            target_metrics['relative_rating'] * 0.6 +
            (1 - abs(target_metrics['relative_price'])) * 0.4
        )
        
        # Determine price elasticity based on business type and market position
        elasticity = self._get_price_elasticity(business_type, market_position['status'])
        
        # Calculate seasonal demand trend
        demand_trend = self._get_seasonal_demand_trend(business_type)
        
        # Calculate base adjustments
        base_adjustment = competitive_strength * 0.15  # Max 15% adjustment
        
        # Calculate final adjustments
        adjustments = {
            'min_adjustment': max(-0.2, base_adjustment - 0.1),  # Max 20% decrease
            'max_adjustment': min(0.3, base_adjustment + 0.15),  # Max 30% increase
            'recommended_adjustment': base_adjustment,
            'competitive_strength': competitive_strength,
            'price_elasticity': elasticity,
            'demand_trend': demand_trend
        }
        
        # Add recommendations
        adjustments['primary_recommendation'] = self._get_dynamic_price_recommendation(
            market_position['status'],
            competitive_strength,
            business_type
        )
        
        adjustments['seasonal_recommendation'] = self._get_seasonal_recommendation(business_type)
        
        return adjustments

    def _get_price_elasticity(self, business_type: str, market_position: str) -> float:
        """Calculate price elasticity based on business type and market position."""
        base_elasticity = {
            'restaurant': 0.8,
            'cafe': 0.9,
            'retail': 0.7,
            'fitness': 0.6,
            'salon': 0.75,
            'hotel': 0.5,
            'service': 0.65,
            'e-commerce': 0.85
        }.get(business_type.lower(), 0.7)
        
        # Adjust based on market position
        position_multiplier = {
            'premium': 0.8,  # Less elastic
            'value_leader': 1.2,  # More elastic
            'competitive': 1.0,
            'overpriced': 1.3,  # Most elastic
            'budget': 1.1
        }.get(market_position, 1.0)
        
        return base_elasticity * position_multiplier

    def _get_seasonal_demand_trend(self, business_type: str) -> str:
        """Get seasonal demand trend based on business type and current season."""
        current_month = datetime.now().month
        season = (
            'winter' if current_month in [12, 1, 2]
            else 'spring' if current_month in [3, 4, 5]
            else 'summer' if current_month in [6, 7, 8]
            else 'fall'
        )
        
        trends = {
            'restaurant': {
                'winter': 'moderate',
                'spring': 'increasing',
                'summer': 'peak',
                'fall': 'moderate'
            },
            'cafe': {
                'winter': 'strong',
                'spring': 'moderate',
                'summer': 'moderate',
                'fall': 'increasing'
            }
        }.get(business_type.lower(), {
            'winter': 'moderate',
            'spring': 'increasing',
            'summer': 'peak',
            'fall': 'moderate'
        })
        
        return trends.get(season, 'moderate')

    def _get_dynamic_price_recommendation(self, market_position: str, 
                                       competitive_strength: float,
                                       business_type: str) -> str:
        """Get specific dynamic pricing recommendation."""
        if market_position == 'premium' and competitive_strength > 0.5:
            return f"Implement premium pricing with dynamic peak-time adjustments"
        elif market_position == 'value_leader':
            return f"Maintain competitive pricing while gradually increasing rates"
        elif market_position == 'overpriced':
            return f"Adjust prices downward and implement targeted promotions"
        elif market_position == 'budget':
            return f"Focus on volume with strategic peak-time price increases"
        else:
            return f"Maintain dynamic pricing based on demand patterns"
    
    async def _analyze_competitors(self, data: Dict[str, Any]) -> AnalysisResult:
        """Analyze competitors and competitive landscape."""
        try:
            competitors = data.get('competitors', [])
            business_type = data.get('business_type', '').lower()
            business_name = data.get('business_name', '')
            
            if not competitors:
                return self._create_error_result("No competitor data available")

            # Calculate competitive metrics
            metrics = {
                'avg_rating': sum(c.get('rating',0) for c in competitors)/len(competitors),
                'avg_price': sum(c.get('price_level',2) for c in competitors)/len(competitors),
                'total_reviews': sum(c.get('review_count',0) for c in competitors)
            }

            # Generate dynamic recommendations
            recs = [
                f"Differentiate through {self._get_unique_value_proposition(business_type)}",
                f"Monitor top competitor: {competitors[0]['name']}",
                self._get_competitive_pricing_strategy(data.get('price_level'), metrics['avg_price'])
            ]

            # Add seasonal competitive strategy
            recs.append(self._get_seasonal_competitive_strategy(business_type))

            return AnalysisResult(
                success=True,
                data={
                    'strengths': [
                        f"Higher than average rating ({data.get('rating',0):.1f} vs {metrics['avg_rating']:.1f})",
                        self._get_market_position_strength(business_type, metrics)
                    ],
                    'weaknesses': [
                        f"Price level {'above' if data.get('price_level',2) > metrics['avg_price'] else 'below'} market average",
                        self._get_competitive_weaknesses(competitors)
                    ],
                    'recommendations': recs,
                    'market_metrics': metrics
                }
            )

        except Exception as e:
            logger.error(f"Competition analysis failed: {str(e)}")
            return self._create_error_result(str(e))

    def _get_business_type_metrics(self, business_type: str) -> List[str]:
        """Get relevant metrics for specific business type."""
        base_metrics = ['rating', 'review_count', 'price_level']
        
        type_specific = {
            'restaurant': ['food_rating', 'service_rating', 'ambiance_rating'],
            'cafe': ['coffee_rating', 'food_rating', 'atmosphere_rating'],
            'fitness': ['equipment_rating', 'trainer_rating', 'cleanliness_rating'],
            'salon': ['service_rating', 'skill_rating', 'ambiance_rating'],
            'hotel': ['room_rating', 'service_rating', 'location_rating'],
            'retail': ['product_rating', 'service_rating', 'store_rating'],
            'service': ['quality_rating', 'reliability_rating', 'value_rating'],
            'e-commerce': ['product_rating', 'delivery_rating', 'support_rating']
        }
        
        return base_metrics + type_specific.get(business_type, [])

    def _get_business_type_insights(self, business_type: str, avg_rating: float, avg_price: float) -> Dict[str, List[str]]:
        """Get business-type specific competitive insights."""
        insights = {
            'restaurant': {
                'strengths': [
                    "Unique culinary offerings",
                    "Prime location for target market",
                    "Distinctive dining experience"
                ],
                'weaknesses': [
                    "High competition in restaurant sector",
                    "Price sensitivity in dining market",
                    "Seasonal demand fluctuations"
                ],
                'opportunities': [
                    "Expand delivery services",
                    "Create unique dining experiences",
                    "Develop loyalty programs"
                ]
            },
            'fitness': {
                'strengths': [
                    "Modern equipment and facilities",
                    "Qualified training staff",
                    "Diverse class offerings"
                ],
                'weaknesses': [
                    "High fixed costs",
                    "Membership retention challenges",
                    "Peak hour capacity constraints"
                ],
                'opportunities': [
                    "Introduce virtual training options",
                    "Create specialized fitness programs",
                    "Develop corporate partnerships"
                ]
            }
            # Add more business types as needed
        }
        
        default_insights = {
            'strengths': [
                "Established market presence",
                "Quality service delivery",
                "Customer satisfaction focus"
            ],
            'weaknesses': [
                "Market competition pressure",
                "Resource optimization needs",
                "Service standardization challenges"
            ],
            'opportunities': [
                "Service expansion potential",
                "Market share growth",
                "Customer experience enhancement"
            ]
        }
        
        return insights.get(business_type, default_insights)

    def _analyze_market_position(self, business_type: str, competitors: List[Dict], rating: float, price_level: int) -> str:
        """Analyze market position based on competitors and business type."""
        top_competitors = sorted(competitors, key=lambda x: x['rating'], reverse=True)[:3]
        price_position = "premium" if price_level > 2.5 else "mid-range" if price_level > 1.5 else "budget"
        
        if rating > top_competitors[0]['rating']:
            return f"Market leader in the {price_position} {business_type} segment with superior ratings"
        elif rating > sum(c['rating'] for c in top_competitors) / 3:
            return f"Strong competitor in the {price_position} {business_type} market"
        else:
            return f"Growing presence in the {price_position} {business_type} sector with opportunity for improvement"

    def _get_competitive_action(self, business_type: str, market_position: str) -> str:
        """Get competitive action based on business type and position."""
        actions = {
            'restaurant': {
                'leader': "Maintain premium positioning with innovative menu items",
                'challenger': "Focus on unique cuisine and dining experience",
                'follower': "Develop distinctive value proposition in food and service"
            },
            'fitness': {
                'leader': "Expand premium services and maintain equipment quality",
                'challenger': "Differentiate with specialized fitness programs",
                'follower': "Focus on member experience and retention"
            }
            # Add more business types
        }
        
        business_actions = actions.get(business_type, {
            'leader': "Maintain market leadership with innovation",
            'challenger': "Focus on service differentiation",
            'follower': "Improve core service quality"
        })
        
        return business_actions.get(market_position, "Develop competitive advantages")

    def _get_seasonal_competitive_strategy(self, business_type: str) -> str:
        """Get seasonal recommendation based on business type."""
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:  # Winter
            seasons = {
                'restaurant': "Introduce winter specials with seasonal pricing",
                'cafe': "Adjust prices for hot beverages and winter items",
                'retail': "Implement winter sale strategies",
                'fitness': "Create new year fitness package pricing",
                'salon': "Promote winter hair care packages",
                'hotel': "Adjust rates for winter tourism",
                'service': "Create winter service packages",
                'e-commerce': "Implement holiday season pricing"
            }
        elif current_month in [3, 4, 5]:  # Spring
            seasons = {
                'restaurant': "Launch spring menu with seasonal pricing",
                'cafe': "Introduce spring beverage specials",
                'retail': "Adjust pricing for spring collection",
                'fitness': "Create spring fitness challenge pricing packages",
                'salon': "Promote spring beauty packages",
                'hotel': "Implement spring break pricing",
                'service': "Launch spring service promotions",
                'e-commerce': "Adjust pricing for spring items"
            }
        elif current_month in [6, 7, 8]:  # Summer
            seasons = {
                'restaurant': "Optimize pricing for outdoor dining",
                'cafe': "Adjust prices for cold beverages",
                'retail': "Implement summer sale strategy",
                'fitness': "Create summer membership specials",
                'salon': "Promote summer beauty packages",
                'hotel': "Optimize peak season pricing",
                'service': "Adjust summer service rates",
                'e-commerce': "Create summer pricing strategy"
            }
        else:  # Fall
            seasons = {
                'restaurant': "Update menu with fall pricing",
                'cafe': "Adjust pricing for fall beverages",
                'retail': "Implement fall pricing strategy",
                'fitness': "Create fall fitness package pricing",
                'salon': "Launch fall beauty specials",
                'hotel': "Adjust rates for fall season",
                'service': "Create fall service packages",
                'e-commerce': "Update pricing for fall items"
            }
        
        return seasons.get(business_type.lower(), "Adjust pricing for seasonal demand")
    
    async def _analyze_market(self, data: Dict[str, Any]) -> AnalysisResult:
        """Analyze market conditions and opportunities."""
        try:
            market_data = await self.data_manager._get_market_data(
                data.get('business_type', ''),
                data.get('location', '')
            )
            
            trends = market_data.get('trends', [])
            opportunities = market_data.get('opportunities', [])

            # Generate dynamic recommendations
            recs = [
                f"Capitalize on: {trends[0]}" if trends else "Monitor market trends",
                f"Priority opportunity: {opportunities[0]}" if opportunities else "Explore new markets"
            ]

            # Add business-specific strategy
            recs.append(self._get_market_strategy(
                data.get('business_type'),
                market_data.get('growth_rate', 0)
            ))

            # Format data according to frontend expectations
            return AnalysisResult(
                success=True,
                data={
                    'market': {
                        'market_size': market_data.get('market_size', 'Medium'),
                        'growth_rate': market_data.get('growth_rate', 0),
                        'market_share': market_data.get('market_share', 0),
                        'trends': trends[:3] if trends else [
                            "Growing demand for quality dining experiences",
                            "Increasing focus on local ingredients",
                            "Rising popularity of online ordering"
                        ],
                        'opportunities': opportunities[:3] if opportunities else [
                            "Expand delivery services",
                            "Develop loyalty programs",
                            "Create unique dining experiences"
                        ]
                    }
                }
            )

        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return self._create_error_result(str(e))
    
    def _create_error_result(self, error: str) -> AnalysisResult:
        """Create an error result."""
        return AnalysisResult(
            success=False,
            error=error
        )
    
    def _create_success_result(self, market_data: MarketData, recommendation: Recommendation) -> AnalysisResult:
        """Create a success result."""
        return AnalysisResult(
            success=True,
            data=AnalysisData(
                market_data=market_data,
                recommendation=recommendation
            )
        )

    def _get_market_strategy(self, business_type: str, growth_rate: float) -> str:
        """Get market strategy based on business type and growth rate."""
        if not business_type:
            return "Develop comprehensive market strategy"
            
        business_type = business_type.lower()
        growth_threshold = 0.05  # 5% growth rate threshold
        
        # High growth strategies
        if growth_rate > growth_threshold:
            strategies = {
                'restaurant': "Expand menu offerings and consider new locations",
                'cafe': "Introduce premium products and expand seating capacity",
                'retail': "Increase inventory and expand product lines",
                'fitness': "Add new classes and upgrade equipment",
                'salon': "Expand service offerings and hire additional staff",
                'hotel': "Upgrade amenities and increase room capacity",
                'service': "Scale operations and add new service lines",
                'e-commerce': "Expand product range and improve logistics"
            }
        # Low/moderate growth strategies
        else:
            strategies = {
                'restaurant': "Focus on customer retention and optimize menu",
                'cafe': "Enhance customer experience and optimize costs",
                'retail': "Optimize inventory and focus on high-margin items",
                'fitness': "Focus on member retention and service quality",
                'salon': "Build customer loyalty and optimize scheduling",
                'hotel': "Focus on guest experience and operational efficiency",
                'service': "Enhance service quality and build relationships",
                'e-commerce': "Optimize operations and improve customer service"
            }
        
        return strategies.get(business_type, "Focus on core competencies and market differentiation")

    def _get_seasonal_recommendation(self, business_type: str) -> str:
        """Get seasonal pricing recommendation based on business type and current season."""
        if not business_type:
            return "Adjust pricing based on seasonal demand"
            
        current_month = datetime.now().month
        business_type = business_type.lower()
        
        # Determine current season
        if current_month in [12, 1, 2]:
            season = 'winter'
        elif current_month in [3, 4, 5]:
            season = 'spring'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
            
        # Define seasonal recommendations for each business type
        seasonal_recommendations = {
            'restaurant': {
                'winter': "Promote winter specials and comfort foods with premium pricing",
                'spring': "Launch seasonal menu with fresh ingredients and moderate pricing",
                'summer': "Optimize outdoor seating and implement peak-hour pricing",
                'fall': "Introduce harvest menu items with dynamic pricing"
            },
            'cafe': {
                'winter': "Focus on hot beverages and seasonal winter drinks",
                'spring': "Introduce spring beverage specials and outdoor seating",
                'summer': "Promote cold drinks and implement peak-time pricing",
                'fall': "Launch seasonal fall beverages with premium pricing"
            },
            'retail': {
                'winter': "Implement holiday season pricing strategy",
                'spring': "Launch spring collection with dynamic pricing",
                'summer': "Optimize summer sale pricing",
                'fall': "Adjust pricing for back-to-school and fall season"
            },
            'fitness': {
                'winter': "New Year resolution membership pricing",
                'spring': "Spring fitness challenge pricing packages",
                'summer': "Summer workout special rates",
                'fall': "Fall fitness program pricing"
            },
            'salon': {
                'winter': "Winter hair care package pricing",
                'spring': "Spring beauty package deals",
                'summer': "Summer style special pricing",
                'fall': "Fall beauty treatment pricing"
            },
            'hotel': {
                'winter': "Winter getaway package rates",
                'spring': "Spring break special pricing",
                'summer': "Peak season dynamic pricing",
                'fall': "Fall weekend getaway rates"
            },
            'service': {
                'winter': "Winter service package pricing",
                'spring': "Spring service special rates",
                'summer': "Summer peak service pricing",
                'fall': "Fall service package deals"
            },
            'e-commerce': {
                'winter': "Holiday season dynamic pricing",
                'spring': "Spring collection launch pricing",
                'summer': "Summer sale pricing strategy",
                'fall': "Fall shopping season pricing"
            }
        }
        
        # Get recommendation for business type and season
        business_recommendations = seasonal_recommendations.get(business_type, {})
        recommendation = business_recommendations.get(season)
        
        if not recommendation:
            # Default recommendations if specific one not found
            default_recommendations = {
                'winter': "Implement winter seasonal pricing strategy",
                'spring': "Adjust pricing for spring season demand",
                'summer': "Optimize summer peak pricing",
                'fall': "Update pricing for fall season"
            }
            recommendation = default_recommendations.get(season)
            
        return recommendation or "Adjust pricing based on seasonal demand"
