"""DeepSeek AI client for dynamic pricing optimization."""

import os
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class DynamicPricingAI:
    """AI-powered dynamic pricing engine."""
    
    def __init__(self):
        """Initialize the dynamic pricing AI."""
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not set")
        self.base_url = "https://api.deepseek.com/v1"
        self.session = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_dynamic_price(
        self,
        business_data: Dict[str, Any],
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        pricing_preferences: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get dynamic pricing recommendation using AI analysis.
        
        Args:
            business_data: Core business information (name, type, location)
            market_data: Real-time market conditions and trends
            competitor_data: Current competitor pricing and strategies
            customer_data: Customer behavior and sentiment
            pricing_preferences: Business owner's pricing preferences and constraints
            
        Returns:
            Dynamic pricing recommendation with real-time insights
        """
        try:
            await self._ensure_session()
            
            # Build dynamic pricing prompt
            prompt = self._build_dynamic_pricing_prompt(
                business_data,
                market_data,
                competitor_data,
                customer_data,
                pricing_preferences
            )
            
            # Get AI-powered pricing recommendation
            async with self.session.post(
                f"{self.base_url}/pricing/dynamic",
                json={
                    "prompt": prompt,
                    "options": {
                        "real_time": True,
                        "currency": self._detect_currency(business_data),
                        "dynamic_factors": True
                    }
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Dynamic pricing error: {response.status} - {error_text}"
                    )
                    return None
                    
                result = await response.json()
                return self._process_dynamic_pricing(result)
                
        except Exception as e:
            logger.error(f"Error in dynamic pricing: {str(e)}", exc_info=True)
            return None
            
    def _build_dynamic_pricing_prompt(
        self,
        business_data: Dict[str, Any],
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        pricing_preferences: Dict[str, Any]
    ) -> str:
        """Build structured prompt for dynamic pricing analysis."""
        return json.dumps({
            "task": "dynamic_pricing_optimization",
            "business_info": {
                "name": business_data.get("name"),
                "type": business_data.get("type"),
                "location": business_data.get("location")
            },
            "real_time_factors": {
                "market_conditions": {
                    "demand_level": market_data.get("current_demand", "medium"),
                    "peak_hours": market_data.get("peak_hours", []),
                    "events": market_data.get("local_events", []),
                    "weather": market_data.get("weather_conditions", {})
                },
                "competitor_prices": {
                    "current_prices": competitor_data.get("live_prices", []),
                    "price_changes": competitor_data.get("recent_changes", []),
                    "promotions": competitor_data.get("active_promotions", [])
                },
                "customer_behavior": {
                    "current_demand": customer_data.get("real_time_demand", "normal"),
                    "sentiment": customer_data.get("current_sentiment", "neutral"),
                    "price_sensitivity": customer_data.get("price_sensitivity", "medium")
                }
            },
            "pricing_constraints": {
                "min_price": pricing_preferences.get("min_price"),
                "max_price": pricing_preferences.get("max_price"),
                "target_margin": pricing_preferences.get("target_margin", 0.3),
                "price_change_limit": pricing_preferences.get("max_price_change", 0.15)
            },
            "optimization_goals": {
                "maximize_revenue": pricing_preferences.get("maximize_revenue", True),
                "maintain_competitiveness": pricing_preferences.get("stay_competitive", True),
                "ensure_profitability": pricing_preferences.get("ensure_profit", True)
            }
        })
        
    def _detect_currency(self, business_data: Dict[str, Any]) -> str:
        """Detect appropriate currency for the business location."""
        try:
            country = business_data.get("location", "").split(",")[-1].strip()
            currency_map = {
                "Spain": "EUR",
                "United States": "USD",
                "United Kingdom": "GBP",
                "Japan": "JPY",
                "Australia": "AUD",
                "Canada": "CAD",
                "Switzerland": "CHF",
                "China": "CNY",
                "European Union": "EUR",
                "India": "INR"
            }
            return currency_map.get(country, "USD")
        except Exception:
            return "USD"
            
    def _process_dynamic_pricing(
        self,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate dynamic pricing response."""
        try:
            pricing_data = response.get("dynamic_pricing", {})
            
            return {
                "current_optimal_price": pricing_data.get("optimal_price"),
                "price_range": {
                    "min": pricing_data.get("min_viable_price"),
                    "max": pricing_data.get("max_viable_price")
                },
                "real_time_factors": {
                    "demand_multiplier": pricing_data.get("demand_factor", 1.0),
                    "competition_multiplier": pricing_data.get("competition_factor", 1.0),
                    "time_multiplier": pricing_data.get("time_factor", 1.0),
                    "event_multiplier": pricing_data.get("event_factor", 1.0)
                },
                "price_adjustments": pricing_data.get("suggested_adjustments", []),
                "timing": {
                    "next_update": pricing_data.get("next_update_time"),
                    "peak_pricing_hours": pricing_data.get("peak_hours", [])
                },
                "insights": pricing_data.get("pricing_insights", []),
                "confidence_score": pricing_data.get("confidence", 0.0),
                "currency": pricing_data.get("currency", "USD"),
                "update_frequency": pricing_data.get("update_frequency", "hourly")
            }
            
        except Exception as e:
            logger.error(f"Error processing dynamic pricing: {str(e)}", exc_info=True)
            return None
            
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None 