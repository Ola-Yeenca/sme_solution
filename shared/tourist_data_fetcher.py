from shared.business_data_fetcher import BusinessDataFetcher
from typing import Dict, Any, List
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TouristAttractionDataFetcher(BusinessDataFetcher):
    """Data fetcher for tourist attractions."""

    def _get_search_params(self, business_name: str) -> Dict[str, Any]:
        """Get search parameters for tourist attraction."""
        return {
            "locationId": "187529",  # Valencia
            "page": "1",
            "currencyCode": "EUR",
            "language": "en_US",
            "searchQuery": business_name
        }

    def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse tourist attraction data from API response."""
        if not data.get('status', False):
            raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")

        attractions = data.get('data', {}).get('data', [])
        if not attractions:
            raise ValueError(f"No attractions found")

        attraction = attractions[0]
        return {
            'name': attraction.get('name', ''),
            'rating': attraction.get('rating', 0.0),
            'reviews_count': attraction.get('reviewsCount', 0),
            'price_level': attraction.get('priceTag', '€€'),
            'category': attraction.get('category', {}).get('name', ''),
            'location': {
                'address': attraction.get('address', ''),
                'latitude': attraction.get('latitude', 0),
                'longitude': attraction.get('longitude', 0)
            }
        }

    def _parse_competitor_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse competitor data from API response."""
        if not data.get('status', False):
            raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")

        attractions = data.get('data', {}).get('data', [])
        competitors = []

        for attraction in attractions[1:6]:  # Skip first one (target business) and get next 5
            competitor = {
                'name': attraction.get('name', ''),
                'rating': attraction.get('rating', 0.0),
                'reviews_count': attraction.get('reviewsCount', 0),
                'price_level': attraction.get('priceTag', '€€'),
                'category': attraction.get('category', {}).get('name', ''),
                'distance_km': attraction.get('distance', 0) / 1000  # Convert meters to kilometers
            }
            competitors.append(competitor)

        return competitors

    def _get_api_url(self) -> str:
        """Get API URL for tourist attractions."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/attraction/searchAttractions"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for tourist attractions."""
        return {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
        }
