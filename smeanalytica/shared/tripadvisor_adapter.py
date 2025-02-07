"""TripAdvisor API adapter implementation."""

import os
import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .data_cache import DataCache

logger = logging.getLogger(__name__)

class TripAdvisorAdapter:
    """Adapter for TripAdvisor Content API."""
    
    def __init__(self):
        """Initialize the TripAdvisor adapter."""
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY environment variable is not set")
            
        self.base_url = "https://tripadvisor16.p.rapidapi.com/api/v1"
        self.cache = DataCache()
        self.cache_duration = timedelta(hours=24)
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
            "Accept": "application/json"
        }
        
        # Rate limiting settings
        self.max_requests_per_second = 5
        self.last_request_time = datetime.now()
    
    async def get_complete_data(self, business_name: str, location: str = None) -> Dict[str, Any]:
        """Get comprehensive business data from TripAdvisor."""
        try:
            # Check cache first
            cache_key = f"tripadvisor_{business_name}_{location}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Search for the business
            search_results = await self._search_location(business_name, location)
            if not search_results or 'data' not in search_results:
                return {}
                
            # Get the first matching result
            location_id = search_results['data'][0].get('location_id')
            if not location_id:
                return {}
                
            # Get detailed business data
            details = await self._get_location_details(location_id)
            reviews = await self._get_reviews(location_id)
            photos = await self._get_photos(location_id)
            
            # Combine all data
            complete_data = {
                'details': details.get('data', {}),
                'reviews': reviews.get('data', []),
                'photos': photos.get('data', []),
                'rating': details.get('data', {}).get('rating', 0),
                'review_count': details.get('data', {}).get('num_reviews', 0),
                'price_level': details.get('data', {}).get('price_level', ''),
                'cuisine': details.get('data', {}).get('cuisine', []),
                'address': details.get('data', {}).get('address_obj', {}),
                'website': details.get('data', {}).get('website', ''),
                'phone': details.get('data', {}).get('phone', ''),
                'hours': details.get('data', {}).get('hours', {}),
                'features': details.get('data', {}).get('amenities', [])
            }
            
            # Cache the data
            self.cache.set(cache_key, complete_data, self.cache_duration)
            
            return complete_data
            
        except Exception as e:
            logger.error(f"Error getting TripAdvisor data for {business_name}: {str(e)}")
            return {}
    
    async def get_competitors(self, business_name: str, location: str = None) -> List[Dict[str, Any]]:
        """Get competitor data from TripAdvisor."""
        try:
            # First get the business details to find its category and location
            business_data = await self.get_complete_data(business_name, location)
            if not business_data:
                return []
                
            # Get nearby restaurants of similar category
            location_id = business_data.get('details', {}).get('location_id')
            if not location_id:
                return []
                
            nearby = await self._get_nearby_locations(location_id)
            if not nearby or 'data' not in nearby:
                return []
                
            competitors = []
            for place in nearby['data']:
                if place.get('name') != business_name:  # Exclude the original business
                    competitor = {
                        'name': place.get('name', ''),
                        'rating': place.get('rating', 0),
                        'review_count': place.get('num_reviews', 0),
                        'price_level': place.get('price_level', ''),
                        'cuisine': place.get('cuisine', []),
                        'distance': place.get('distance', 0),
                        'location': {
                            'latitude': place.get('latitude', 0),
                            'longitude': place.get('longitude', 0),
                            'address': place.get('address_obj', {})
                        }
                    }
                    competitors.append(competitor)
            
            return competitors
            
        except Exception as e:
            logger.error(f"Error getting TripAdvisor competitors for {business_name}: {str(e)}")
            return []
    
    async def _search_location(self, query: str, location: str = None) -> Dict[str, Any]:
        """Search for a location on TripAdvisor."""
        endpoint = f"{self.base_url}/location/search"
        params = {
            "searchQuery": f"{query} {location}" if location else query,
            "language": "en"
        }
        return await self._make_request(endpoint, params)
    
    async def _get_location_details(self, location_id: str) -> Dict[str, Any]:
        """Get detailed information about a location."""
        endpoint = f"{self.base_url}/location/{location_id}/details"
        return await self._make_request(endpoint)
    
    async def _get_reviews(self, location_id: str) -> Dict[str, Any]:
        """Get reviews for a location."""
        endpoint = f"{self.base_url}/location/{location_id}/reviews"
        params = {
            "limit": 100,  # Maximum allowed by API
            "language": "en"
        }
        return await self._make_request(endpoint, params)
    
    async def _get_photos(self, location_id: str) -> Dict[str, Any]:
        """Get photos for a location."""
        endpoint = f"{self.base_url}/location/{location_id}/photos"
        params = {
            "limit": 50  # Maximum allowed by API
        }
        return await self._make_request(endpoint, params)
    
    async def _get_nearby_locations(self, location_id: str) -> Dict[str, Any]:
        """Get nearby locations."""
        endpoint = f"{self.base_url}/location/{location_id}/nearby_search"
        params = {
            "radius": 5,  # 5 km radius
            "radiusUnit": "km",
            "limit": 30
        }
        return await self._make_request(endpoint, params)
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a rate-limited request to the TripAdvisor API."""
        # Implement rate limiting
        now = datetime.now()
        time_since_last_request = (now - self.last_request_time).total_seconds()
        if time_since_last_request < (1 / self.max_requests_per_second):
            await asyncio.sleep((1 / self.max_requests_per_second) - time_since_last_request)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=self.headers, params=params) as response:
                    self.last_request_time = datetime.now()
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limit exceeded. Waiting {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                        return await self._make_request(endpoint, params)  # Retry the request
                    else:
                        logger.error(f"TripAdvisor API error: {response.status} - {await response.text()}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error making TripAdvisor API request: {str(e)}")
            return {}
