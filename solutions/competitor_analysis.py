"""Competitor analysis for businesses."""

import os
from typing import Dict, Any, List
import requests

from shared.business_data_fetcher import BusinessDataFetcher
from shared.ai_model_config import AIModel, ModelConfig

class CompetitorAnalyzer:
    """Analyzer for competitor analysis."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher):
        """Initialize with a data fetcher."""
        self.data_fetcher = data_fetcher
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for competitor analysis
        self.model = ModelConfig.get_recommended_model("competitor_analysis")
        self.model_config = ModelConfig.get_model_config(self.model)

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
        """Get AI-powered competitor analysis using Claude-3."""
        try:
            # Create detailed prompt
            prompt = """
            As a competitive analysis expert, provide a comprehensive competitor analysis:
            
            BUSINESS INFO:
            - Name: {name}
            - Rating: {rating}/5.0
            - Reviews: {reviews}
            - Price Level: {price_level}
            
            COMPETITORS:
            {competitors_info}
            
            Please provide a detailed competitive analysis including:
            1. MARKET POSITION
            - Competitive landscape overview
            - Market share analysis
            - Positioning strategy
            
            2. COMPETITIVE ADVANTAGES
            - Key differentiators
            - Unique selling propositions
            - Service quality comparison
            
            3. COMPETITOR STRENGTHS
            - Best practices identified
            - Superior offerings
            - Customer preferences
            
            4. MARKET OPPORTUNITIES
            - Underserved segments
            - Service gaps
            - Growth potential
            
            5. STRATEGIC RECOMMENDATIONS
            - Short-term tactics
            - Long-term strategy
            - Performance metrics
            
            Format the response in clear sections with bullet points.
            Focus on actionable insights and specific examples.
            """
            
            # Format competitors info
            competitors_info = "\n".join(
                "- {name}: Rating {rating}/5.0, Reviews {reviews}, Price Level {price_level}, Distance: {distance:.1f}km".format(
                    name=comp['name'],
                    rating=comp['rating'],
                    reviews=comp['reviews_count'],
                    price_level=comp['price_level'],
                    distance=comp.get('distance_km', 0)
                )
                for comp in competitors[:5]  # Top 5 competitors
            )
            
            # Format the prompt with business data
            formatted_prompt = prompt.format(
                name=business_data.get('name', 'Unknown'),
                rating=business_data.get('rating', 0),
                reviews=business_data.get('reviews_count', 0),
                price_level=business_data.get('price_level', '€'),
                competitors_info=competitors_info
            )
            
            # Make API request with the configured model
            response = requests.post(
                url=self.model_config["url"],
                headers={
                    **self.model_config["headers"],
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model_config["model"],
                    "messages": [{"role": "user", "content": formatted_prompt}]
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to AI service: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating competitor analysis: {str(e)}")