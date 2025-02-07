"""Google Places data fetcher implementation."""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from requests.exceptions import RequestException
from cachetools import TTLCache, cached

from smeanalytica.config.business_types import BusinessType, API_ENDPOINTS
from smeanalytica.shared.exceptions import (
    APIError,
    ValidationError,
    ResourceNotFoundError
)

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL = 3600  # 1 hour
CACHE_MAXSIZE = 100
place_details_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)

class GoogleDataFetcher:
    """Data fetcher implementation using Google Places API."""
    
    BASE_URL = "https://maps.googleapis.com/maps/api/place"
    RATE_LIMIT_DELAY = 0.1  # 100ms delay between requests
    
    def __init__(self, business_type: Optional[BusinessType] = None):
        """Initialize the data fetcher."""
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValidationError("Google Places API key is not configured")
        self.business_type = business_type
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()
        
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a rate-limited request to the Google Places API."""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data
            elif data.get('status') == 'ZERO_RESULTS':
                raise ResourceNotFoundError("No results found")
            elif data.get('status') == 'OVER_QUERY_LIMIT':
                logger.error("Google Places API quota exceeded")
                raise APIError("API quota exceeded")
            else:
                logger.error(f"Google Places API error: {data.get('status')}")
                raise APIError(f"API error: {data.get('status')}")
                
        except RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIError(f"Failed to fetch data: {str(e)}")
            
    @cached(cache=place_details_cache)
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a place."""
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'name,rating,user_ratings_total,price_level,formatted_address,geometry,reviews,opening_hours,website'
        }
        return self._make_request('details/json', params)
        
    def search_places(self, query: str, location: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Search for places using the Places API."""
        params = {
            'query': query,
            'key': self.api_key,
            'type': self.business_type.value if self.business_type else None
        }
        
        if location:
            params.update({
                'location': f"{location['lat']},{location['lng']}",
                'radius': '5000'  # 5km radius
            })
            
        data = self._make_request('textsearch/json', params)
        return [self._parse_place_data(place) for place in data.get('results', [])]
        
    def _parse_place_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse place data from API response."""
        return {
            'place_id': data.get('place_id'),
            'name': data.get('name'),
            'rating': data.get('rating', 0.0),
            'user_ratings_total': data.get('user_ratings_total', 0),
            'price_level': data.get('price_level', 0),
            'location': {
                'lat': data.get('geometry', {}).get('location', {}).get('lat', 0),
                'lng': data.get('geometry', {}).get('location', {}).get('lng', 0),
                'address': data.get('formatted_address', '')
            }
        }

    def get_business_data(self, business_name: str) -> Dict[str, Any]:
        """Get detailed business data."""
        # Search for the business
        search_response = self.search_places(business_name)
        
        if not search_response:
            raise APIError(f"Business '{business_name}' not found")
            
        # Get detailed information
        place_id = search_response[0]['place_id']
        details_response = self.get_place_details(place_id)
        
        business_data = self._parse_place_data(details_response)
        return business_data
        
    def get_competitors(self, business_name: str, radius_meters: int = 5000) -> List[Dict[str, Any]]:
        """Get competitor data within specified radius."""
        # Get business location first
        business_data = self.get_business_data(business_name)
        if not business_data:
            raise APIError(f"Could not find location for business '{business_name}'")
            
        # Search for competitors
        competitor_response = self.search_places(business_name, business_data['location'])
        
        competitors = [self._parse_place_data(place) for place in competitor_response]
        return competitors
