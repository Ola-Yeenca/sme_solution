"""Competitor analysis for businesses."""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from smeanalytica.shared.business_data_fetcher import BusinessDataFetcher
from smeanalytica.config.business_types import BusinessType
from smeanalytica.config.analysis_types import AnalysisType

class CompetitorAnalyzer:
    """Analyzer for competitor analysis."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher, business_type: Optional[BusinessType] = None):
        """Initialize with a data fetcher and optional business type."""
        self.data_fetcher = data_fetcher
        self.business_type = business_type
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for competitor analysis
        self.model = AnalysisType.COMPETITOR_ANALYSIS
        self.model_config = AnalysisType.get_model_config(self.model)

    def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze competitors for a business."""
        try:
            # Get business details and competitors
            business_data = self.data_fetcher.get_business_details(business_name)
            competitors = self.data_fetcher.get_competitors(business_name)
            
            # Get AI analysis using Claude-3
            analysis = self._get_ai_analysis(business_data, competitors)
            
            return {
                'business_info': {
                    'name': business_name,
                    'rating': business_data['rating'],
                    'reviews_count': business_data['reviews_count'],
                    'price_level': business_data['price_level']
                },
                'competitors': [
                    {
                        'name': comp['name'],
                        'rating': comp['rating'],
                        'reviews_count': comp['reviews_count'],
                        'price_level': comp['price_level'],
                        'distance_km': comp['distance_km']
                    } for comp in competitors[:5]  # Top 5 competitors
                ],
                'competitor_analysis': analysis
            }
            
        except Exception as e:
            raise Exception(f"Error in competitor analysis: {str(e)}")

    def _get_ai_analysis(self, business_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> str:
        """Get AI-powered competitor analysis."""
        try:
            # Format business data
            business_info = (
                f"Business Profile:\n"
                f"- Name: {business_data['name']}\n"
                f"- Rating: {business_data['rating']}/5.0\n"
                f"- Reviews: {business_data['reviews_count']}\n"
                f"- Price Level: {business_data['price_level']}\n"
                f"- Market Share: {business_data.get('local_market_share', 0)*100:.1f}%\n"
                f"- Cuisine: {', '.join(business_data.get('cuisine', []))}"
            )
            
            # Format competitor data
            competitors_info = "Competitors:\n" + "\n".join(
                f"- {comp['name']}:\n"
                f"  * Rating: {comp['rating']}/5.0\n"
                f"  * Reviews: {comp['reviews_count']}\n"
                f"  * Price Level: {comp['price_level']}\n"
                f"  * Distance: {comp['distance_km']:.1f}km"
                for comp in competitors[:5]
            )
            
            # Create comprehensive analysis prompt
            prompt = f"""As a strategic business analyst, provide a detailed competitor analysis for this business.

{business_info}

{competitors_info}

Please provide a comprehensive analysis including:

1. Competitive Position Assessment
   - Market positioning
   - Unique selling propositions
   - Brand strength analysis
   - Price-value relationship

2. Competitor Strengths & Weaknesses
   - Service quality comparison
   - Price point analysis
   - Location advantages/disadvantages
   - Customer satisfaction metrics

3. Market Opportunities
   - Underserved segments
   - Service gaps
   - Geographic expansion potential
   - Menu/offering optimization

4. Competitive Advantages
   - Current advantages to leverage
   - Potential new advantages to develop
   - Ways to differentiate

5. Threat Mitigation
   - Direct competition threats
   - Indirect competition
   - Market trends impact
   - Risk mitigation strategies

6. Action Plan
   - Short-term tactics (0-3 months)
   - Medium-term strategy (3-12 months)
   - Long-term positioning (1-3 years)
   - Resource allocation recommendations

Focus on actionable insights that will help the business strengthen its competitive position while maintaining profitability."""

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