"""Pricing routes for the SME Analytica API."""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...core.pricing.pricing_engine import DynamicPricingEngine
from ...core.pricing.data_fetcher import PricingDataFetcher
from ...shared.decorators import require_api_key, rate_limit, cache
from ...core.models.model_manager import ModelManager

logger = logging.getLogger(__name__)

router = APIRouter()
pricing_engine = DynamicPricingEngine()
data_fetcher = PricingDataFetcher()
model_manager = ModelManager()

class SimplePricingRequest(BaseModel):
    """Simplified request model for autonomous pricing analysis."""
    business_name: str = Field(..., description="Name of the business")
    business_type: str = Field(..., description="Type of business (e.g., restaurant, retail)")

class PricingResponse(BaseModel):
    """Response model for pricing analysis."""
    suggested_price: float = Field(..., description="Suggested optimal price")
    min_price: float = Field(..., description="Minimum recommended price")
    max_price: float = Field(..., description="Maximum recommended price")
    confidence_score: float = Field(..., description="Confidence in the recommendation (0.0-1.0)")
    insights: list[str] = Field(..., description="Pricing insights and explanations")
    market_factors: Dict[str, Any] = Field(..., description="Market factors affecting price")
    competitor_analysis: Dict[str, Any] = Field(..., description="Competitor analysis results")
    customer_sentiment: Dict[str, Any] = Field(..., description="Customer sentiment analysis")
    auto_detected_costs: Dict[str, float] = Field(..., description="Automatically detected business costs")
    suggested_margin: float = Field(..., description="AI-suggested optimal profit margin")

@router.post("/analyze-pricing", response_model=PricingResponse)
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
@cache(ttl=300)  # 5 minutes cache
async def analyze_pricing(request: SimplePricingRequest) -> Dict[str, Any]:
    """
    Analyze and recommend optimal pricing based on market conditions.
    
    This endpoint:
    1. Automatically fetches business location and details
    2. Retrieves market, competitor, and customer data
    3. Uses AI to determine optimal costs and margins
    4. Generates comprehensive pricing recommendations
    
    The recommendation includes:
    - Suggested price point
    - Valid price range
    - Market insights
    - Competitor analysis
    - Customer sentiment impact
    - Auto-detected costs
    - AI-suggested margins
    
    Rate limit: 100 requests per hour
    Cache TTL: 5 minutes
    """
    try:
        # 1. Auto-detect business location and details
        business_data = await data_fetcher.get_business_data(request.business_name)
        if not business_data:
            raise HTTPException(status_code=404, detail="Business not found")
            
        location = business_data.get('location')
        
        # 2. Fetch market data
        market_data = await data_fetcher.get_market_data(
            request.business_type,
            location
        )
        
        # 3. Get competitor data
        competitor_data = await data_fetcher.get_competitor_data(
            request.business_name,
            request.business_type,
            location
        )
        
        # 4. Get customer sentiment data
        customer_data = await data_fetcher.get_customer_data(
            request.business_name,
            request.business_type
        )
        
        # 5. Use AI to analyze costs and determine optimal margins
        model = await model_manager.get_model('pricing_optimization')
        if not model:
            raise HTTPException(status_code=500, detail="Pricing model not available")
            
        # 6. Get comprehensive price recommendation
        recommendation = await pricing_engine.get_autonomous_recommendation(
            business_data,
            market_data,
            competitor_data,
            customer_data,
            model
        )
        
        if not recommendation:
            raise HTTPException(
                status_code=500,
                detail="Could not generate pricing recommendation"
            )
            
        return recommendation
        
    except Exception as e:
        logger.error(f"Error analyzing pricing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing pricing: {str(e)}"
        )
