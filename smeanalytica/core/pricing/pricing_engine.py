"""Dynamic pricing engine for SME Analytica."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from ...shared.deepseek_client import DynamicPricingAI as DeepSeekClient

logger = logging.getLogger(__name__)

@dataclass
class PriceRecommendation:
    """Price recommendation with detailed insights."""
    suggested_price: float
    min_price: float
    max_price: float
    confidence_score: float
    factors: Dict[str, Any]
    insights: List[str]
    timestamp: str

class DynamicPricingEngine:
    """Engine for dynamic pricing analysis and recommendations."""
    
    def __init__(self):
        """Initialize the pricing engine."""
        self.deepseek = DeepSeekClient()
        self.market_trends = {}
        self.competitor_cache = {}
        
    async def get_autonomous_recommendation(
        self,
        business_data: Dict[str, Any],
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        model: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get autonomous pricing recommendation using AI analysis.
        
        Args:
            business_data: Business information and metrics
            market_data: Market analysis data
            competitor_data: Competitor analysis data
            customer_data: Customer sentiment data
            model: AI model configuration
            
        Returns:
            Comprehensive pricing recommendation or None if analysis fails
        """
        try:
            # Use DeepSeek AI for analysis
            recommendation = await self.deepseek.analyze_pricing(
                business_data,
                market_data,
                competitor_data,
                customer_data
            )
            
            if not recommendation:
                logger.error("Failed to get pricing recommendation from DeepSeek")
                return None
                
            # Validate recommendation
            if not self._validate_recommendation(recommendation):
                logger.error("Invalid pricing recommendation received")
                return None
                
            # Enhance recommendation with additional insights
            enhanced = self._enhance_recommendation(
                recommendation,
                business_data,
                market_data
            )
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in pricing engine: {str(e)}", exc_info=True)
            return None
            
    def _validate_recommendation(
        self,
        recommendation: Dict[str, Any]
    ) -> bool:
        """
        Validate pricing recommendation.
        
        Args:
            recommendation: Pricing recommendation to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "suggested_price",
            "min_price",
            "max_price",
            "confidence_score",
            "insights",
            "market_factors",
            "competitor_analysis",
            "customer_sentiment",
            "auto_detected_costs",
            "suggested_margin"
        ]
        
        # Check all required fields exist
        for field in required_fields:
            if field not in recommendation:
                logger.error(f"Missing required field: {field}")
                return False
                
        # Validate price ranges
        if not (
            recommendation["min_price"] <= recommendation["suggested_price"] <= recommendation["max_price"]
        ):
            logger.error("Invalid price range")
            return False
            
        # Validate confidence score
        if not (0 <= recommendation["confidence_score"] <= 1):
            logger.error("Invalid confidence score")
            return False
            
        return True
        
    def _enhance_recommendation(
        self,
        recommendation: Dict[str, Any],
        business_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance pricing recommendation with additional insights.
        
        Args:
            recommendation: Base pricing recommendation
            business_data: Business information
            market_data: Market analysis data
            
        Returns:
            Enhanced recommendation
        """
        try:
            # Add market context
            recommendation["market_context"] = {
                "market_size": market_data.get("market_size"),
                "growth_rate": market_data.get("growth_rate"),
                "market_trends": market_data.get("trends", [])
            }
            
            # Add business context
            recommendation["business_context"] = {
                "business_type": business_data.get("type"),
                "location": business_data.get("location"),
                "target_customer_segment": business_data.get("target_segment")
            }
            
            # Add implementation steps
            recommendation["implementation_steps"] = [
                {
                    "step": 1,
                    "action": "Review suggested pricing structure",
                    "details": "Analyze the suggested price points and margins"
                },
                {
                    "step": 2,
                    "action": "Evaluate market positioning",
                    "details": "Consider how the suggested pricing aligns with market position"
                },
                {
                    "step": 3,
                    "action": "Plan implementation timeline",
                    "details": "Develop a timeline for implementing price changes"
                }
            ]
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error enhancing recommendation: {str(e)}", exc_info=True)
            return recommendation  # Return original if enhancement fails
            
    async def close(self):
        """Close the pricing engine."""
        await self.deepseek.close()

    async def get_price_recommendation(
        self,
        business_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None,
        competitor_data: Optional[Dict[str, Any]] = None,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> PriceRecommendation:
        """
        Generate price recommendations based on business and market data.
        
        Args:
            business_data: Core business information including costs and current prices
            market_data: Optional market trend data
            competitor_data: Optional competitor pricing data
            customer_data: Optional customer sentiment data
            
        Returns:
            PriceRecommendation with suggested prices and detailed insights
        """
        try:
            # 1. Calculate base price from costs
            base_price = self._calculate_base_price(business_data)
            
            # 2. Adjust for market factors
            market_adjustment = self._analyze_market_factors(market_data)
            
            # 3. Consider competitor pricing
            competitor_adjustment = self._analyze_competitor_pricing(competitor_data)
            
            # 4. Factor in customer sentiment
            sentiment_adjustment = self._analyze_customer_sentiment(customer_data)
            
            # 5. Calculate final price recommendation
            suggested_price = base_price * (1 + sum([
                market_adjustment,
                competitor_adjustment,
                sentiment_adjustment
            ]))
            
            # 6. Calculate price bounds
            min_price = self._calculate_min_price(business_data, base_price)
            max_price = self._calculate_max_price(business_data, competitor_data)
            
            # 7. Generate insights
            insights = self._generate_pricing_insights(
                business_data,
                market_data,
                competitor_data,
                customer_data,
                base_price,
                suggested_price
            )
            
            # 8. Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                market_data,
                competitor_data,
                customer_data
            )
            
            return PriceRecommendation(
                suggested_price=round(suggested_price, 2),
                min_price=round(min_price, 2),
                max_price=round(max_price, 2),
                confidence_score=confidence_score,
                factors={
                    'base_price': base_price,
                    'market_adjustment': market_adjustment,
                    'competitor_adjustment': competitor_adjustment,
                    'sentiment_adjustment': sentiment_adjustment
                },
                insights=insights,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating price recommendation: {str(e)}")
            raise
            
    def _calculate_base_price(self, business_data: Dict[str, Any]) -> float:
        """Calculate base price from costs and minimum profit margin."""
        costs = business_data.get('costs', {})
        target_margin = business_data.get('target_margin', 0.3)
        
        total_cost = sum(costs.values())
        return total_cost / (1 - target_margin)
        
    def _analyze_market_factors(
        self,
        market_data: Optional[Dict[str, Any]]
    ) -> float:
        """Analyze market factors and return price adjustment factor."""
        if not market_data:
            return 0.0
            
        adjustments = []
        
        # Seasonal demand
        if seasonal_factor := market_data.get('seasonal_demand', 1.0):
            adjustments.append(0.1 * (seasonal_factor - 1))
            
        # Market growth
        if growth_rate := market_data.get('market_growth', 0.0):
            adjustments.append(0.05 * growth_rate)
            
        # Local events impact
        if event_impact := market_data.get('event_impact', 0.0):
            adjustments.append(0.05 * event_impact)
            
        return sum(adjustments)
        
    def _analyze_competitor_pricing(
        self,
        competitor_data: Optional[Dict[str, Any]]
    ) -> float:
        """Analyze competitor pricing and return price adjustment factor."""
        if not competitor_data:
            return 0.0
            
        competitor_prices = competitor_data.get('prices', [])
        if not competitor_prices:
            return 0.0
            
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
        our_price = competitor_data.get('our_price', avg_competitor_price)
        
        # Adjust towards average competitor price
        price_gap = (avg_competitor_price - our_price) / our_price
        return 0.2 * price_gap  # Adjust 20% towards competitor average
        
    def _analyze_customer_sentiment(
        self,
        customer_data: Optional[Dict[str, Any]]
    ) -> float:
        """Analyze customer sentiment and return price adjustment factor."""
        if not customer_data:
            return 0.0
            
        sentiment_score = customer_data.get('sentiment_score', 0.0)
        review_score = customer_data.get('review_score', 0.0)
        
        # Positive sentiment and reviews allow for higher prices
        sentiment_impact = 0.1 * (sentiment_score - 0.5)
        review_impact = 0.1 * (review_score - 3.5) / 1.5
        
        return sentiment_impact + review_impact
        
    def _calculate_min_price(
        self,
        business_data: Dict[str, Any],
        base_price: float
    ) -> float:
        """Calculate minimum viable price."""
        costs = business_data.get('costs', {})
        total_cost = sum(costs.values())
        min_margin = business_data.get('min_margin', 0.1)
        
        return total_cost / (1 - min_margin)
        
    def _calculate_max_price(
        self,
        business_data: Dict[str, Any],
        competitor_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate maximum recommended price."""
        base_max = self._calculate_min_price(business_data, 0) * 2
        
        if competitor_data and (competitor_prices := competitor_data.get('prices')):
            competitor_max = max(competitor_prices) * 1.2
            return min(base_max, competitor_max)
            
        return base_max
        
    def _generate_pricing_insights(
        self,
        business_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]],
        competitor_data: Optional[Dict[str, Any]],
        customer_data: Optional[Dict[str, Any]],
        base_price: float,
        suggested_price: float
    ) -> List[str]:
        """Generate human-readable insights about the price recommendation."""
        insights = []
        
        # Cost structure insights
        costs = business_data.get('costs', {})
        total_cost = sum(costs.values())
        margin = (suggested_price - total_cost) / suggested_price
        insights.append(
            f"Recommended price provides a {margin:.1%} profit margin based on your costs"
        )
        
        # Market insights
        if market_data:
            if seasonal_factor := market_data.get('seasonal_demand'):
                if seasonal_factor > 1:
                    insights.append(
                        f"High seasonal demand supports a {(seasonal_factor-1):.1%} price increase"
                    )
                else:
                    insights.append(
                        f"Low seasonal demand suggests a {(1-seasonal_factor):.1%} price decrease"
                    )
                    
        # Competitor insights
        if competitor_data and (competitor_prices := competitor_data.get('prices')):
            avg_competitor = sum(competitor_prices) / len(competitor_prices)
            diff = (suggested_price - avg_competitor) / avg_competitor
            if abs(diff) > 0.05:
                insights.append(
                    f"Suggested price is {abs(diff):.1%} {'above' if diff > 0 else 'below'} "
                    f"average competitor price"
                )
                
        # Customer insights
        if customer_data:
            sentiment = customer_data.get('sentiment_score', 0.5)
            if sentiment > 0.6:
                insights.append(
                    "Strong customer sentiment supports maintaining current pricing"
                )
            elif sentiment < 0.4:
                insights.append(
                    "Lower customer sentiment suggests reviewing value proposition"
                )
                
        return insights
        
    def _calculate_confidence_score(
        self,
        market_data: Optional[Dict[str, Any]],
        competitor_data: Optional[Dict[str, Any]],
        customer_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the price recommendation."""
        score = 0.5  # Base confidence
        
        # More data = higher confidence
        if market_data and market_data.get('seasonal_demand') is not None:
            score += 0.2
            
        if competitor_data and competitor_data.get('prices'):
            score += 0.2
            
        if customer_data and customer_data.get('sentiment_score') is not None:
            score += 0.1
            
        return min(score, 1.0)  # Cap at 1.0
