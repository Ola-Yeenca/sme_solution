"""Dynamic pricing routes for real-time price optimization."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ...core.pricing.dynamic_pricing_engine import DynamicPricingEngine
from ...shared.decorators import require_api_key, rate_limit, cache

logger = logging.getLogger(__name__)

router = APIRouter()
pricing_engine = DynamicPricingEngine()

class PricingPreferences(BaseModel):
    """Business owner's pricing preferences."""
    min_price: Optional[float] = Field(None, description="Minimum acceptable price")
    max_price: Optional[float] = Field(None, description="Maximum acceptable price")
    target_margin: float = Field(0.3, description="Target profit margin (0.0-1.0)")
    max_price_change: float = Field(0.15, description="Maximum allowed price change (0.0-1.0)")
    maximize_revenue: bool = Field(True, description="Prioritize revenue maximization")
    stay_competitive: bool = Field(True, description="Maintain competitive pricing")
    ensure_profit: bool = Field(True, description="Ensure minimum profit margins")

class DynamicPricingRequest(BaseModel):
    """Request model for dynamic pricing."""
    business_name: str = Field(..., description="Name of the business")
    business_type: str = Field(..., description="Type of business (e.g., restaurant, retail)")
    preferences: PricingPreferences = Field(..., description="Pricing preferences")

class PriceRange(BaseModel):
    """Price range model."""
    min: float = Field(..., description="Minimum viable price")
    max: float = Field(..., description="Maximum viable price")

class RealTimeFactors(BaseModel):
    """Real-time pricing factors."""
    demand_multiplier: float = Field(..., description="Current demand impact")
    competition_multiplier: float = Field(..., description="Competitor price impact")
    time_multiplier: float = Field(..., description="Time of day impact")
    event_multiplier: float = Field(..., description="Local events impact")

class PriceTiming(BaseModel):
    """Price timing information."""
    next_update: str = Field(..., description="Next price update time")
    peak_pricing_hours: List[str] = Field(..., description="Peak pricing hours")

class PriceTrends(BaseModel):
    """Price trend analysis."""
    trend: str = Field(..., description="Current price trend")
    volatility: str = Field(..., description="Price volatility level")

class HistoricalContext(BaseModel):
    """Historical pricing context."""
    price_volatility: float = Field(..., description="Historical price volatility")
    peak_prices: Dict[str, float] = Field(..., description="Historical peak prices")
    optimal_times: List[str] = Field(..., description="Historically optimal pricing times")

class DynamicPricingResponse(BaseModel):
    """Response model for dynamic pricing."""
    current_optimal_price: float = Field(..., description="Current optimal price")
    price_range: PriceRange = Field(..., description="Valid price range")
    real_time_factors: RealTimeFactors = Field(..., description="Real-time pricing factors")
    price_adjustments: List[Dict[str, Any]] = Field(..., description="Suggested price adjustments")
    timing: PriceTiming = Field(..., description="Price timing information")
    insights: List[str] = Field(..., description="Pricing insights and explanations")
    confidence_score: float = Field(..., description="Confidence in recommendation (0.0-1.0)")
    currency: str = Field(..., description="Price currency")
    update_frequency: str = Field(..., description="Price update frequency")
    price_trends: Optional[PriceTrends] = Field(None, description="Price trend analysis")
    historical_context: Optional[HistoricalContext] = Field(None, description="Historical pricing context")

@router.post("/optimize", response_model=DynamicPricingResponse)
@require_api_key
@rate_limit(max_requests=60, window_seconds=60)  # 1 request per second
@cache(ttl_seconds=60)  # 1 minute cache
async def optimize_price(request: Request) -> Dict[str, Any]:
    """
    Get real-time optimal pricing recommendation.
    
    This endpoint:
    1. Analyzes real-time market conditions
    2. Considers competitor pricing
    3. Factors in customer behavior
    4. Applies business preferences
    5. Provides dynamic price recommendations
    
    The response includes:
    - Current optimal price
    - Valid price range
    - Real-time pricing factors
    - Suggested adjustments
    - Timing recommendations
    - Historical context
    - Confidence score
    
    Rate limit: 60 requests per minute
    Cache TTL: 1 minute
    """
    try:
        data = await request.json()
        if not data:
            raise HTTPException(
                status_code=400,
                detail="No data provided"
            )
        
        required_fields = ["business_name", "business_type", "preferences"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Get optimal price recommendation
        recommendation = await pricing_engine.get_optimal_price(
            data["business_name"],
            data["business_type"],
            data["preferences"]
        )
        
        if not recommendation:
            raise HTTPException(
                status_code=500,
                detail="Could not generate price recommendation"
            )
            
        return recommendation
        
    except Exception as e:
        logger.error(f"Error optimizing price: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing price: {str(e)}"
        ) 