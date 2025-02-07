"""Google Places API adapter for fetching business data."""

import os
import logging
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..config.data_sources import DataSourceConfig

class GooglePlacesError(Exception):
    """Custom exception for Google Places API errors."""
    pass

class APIRateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if we're over the rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove calls older than 1 minute
        self.calls = [call for call in self.calls if call > minute_ago]
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.calls.append(now)

class GooglePlacesAdapter:
    """Adapter for Google Places API integration."""
    
    def __init__(self):
        """Initialize the Google Places adapter."""
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            logging.error("GOOGLE_PLACES_API_KEY environment variable is not set")
            raise GooglePlacesError(
                "Google Places API key is not configured. Please set the GOOGLE_PLACES_API_KEY environment variable. "
                "You can get an API key from the Google Cloud Console: https://console.cloud.google.com/apis/credentials"
            )
        
        self.base_url = "https://places.googleapis.com/v1/places"
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "*"
        }
        
        # Initialize rate limiter
        self.rate_limiter = APIRateLimiter(
            DataSourceConfig.RATE_LIMITS['google_places']
        )
        
    async def get_complete_data(self, business_name: str) -> Dict[str, Any]:
        """Get complete business data from Google Places API."""
        try:
            self.rate_limiter.wait_if_needed()
            
            async with aiohttp.ClientSession() as session:
                # First, search for the business
                search_url = f"{self.base_url}:searchText"
                search_data = {
                    "textQuery": business_name,
                    "locationBias": {
                        "circle": {
                            "center": {
                                "latitude": 39.4699,  # Valencia, Spain coordinates
                                "longitude": -0.3763
                            },
                            "radius": 5000.0  # 5km radius
                        }
                    }
                }
                
                start_time = time.time()
                async with session.post(search_url, json=search_data, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'places' in data and len(data['places']) > 0:
                            place = data['places'][0]
                            
                            # Format the response
                            result = {
                                'name': place.get('displayName', {}).get('text', ''),
                                'rating': place.get('rating', 0.0),
                                'total_ratings': place.get('userRatingCount', 0),
                                'price_level': place.get('priceLevel', ''),
                                'location': {
                                    'address': place.get('formattedAddress', ''),
                                    'lat': place.get('location', {}).get('latitude', 0),
                                    'lng': place.get('location', {}).get('longitude', 0)
                                },
                                'categories': [
                                    type.get('displayName', {}).get('text', '')
                                    for type in place.get('types', [])
                                ],
                                'source': 'google_places'
                            }
                            
                            logging.info(f"Google Places API complete_data operation completed in {time.time() - start_time:.2f}s")
                            return result
                        else:
                            logging.warning(f"Could not find business: {business_name}")
                            return {}
                    else:
                        error_msg = await response.text()
                        raise GooglePlacesError(f"API request failed: {response.status}, message='{error_msg}', url='{search_url}'")
                        
        except Exception as e:
            logging.error(f"Error getting Google Places data: {str(e)}")
            raise GooglePlacesError(f"Error getting Google Places data: {str(e)}")

    async def get_competitors(self, business_name: str, location: str = "Valencia, Spain") -> List[Dict[str, Any]]:
        """Get competitors for a business in the same area.
        
        Args:
            business_name: Name of the business
            location: Location to search in
            
        Returns:
            List of competitor businesses
        """
        try:
            # First get the target business to get its location and category
            business_data = await self.search_business(business_name, location)
            if not business_data:
                logging.warning(f"Could not find business: {business_name} in {location}")
                return []
                
            # Get the business location
            business_location = business_data.get('location', {})
            if not business_location:
                logging.warning(f"No location data found for business: {business_name}")
                return []
                
            # Search for nearby businesses of the same type
            search_url = f"{self.base_url}:searchNearby"
            payload = {
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": business_location['latitude'],
                            "longitude": business_location['longitude']
                        },
                        "radius": 2000.0  # 2km radius
                    }
                },
                "rankPreference": "RATING",
                "maxResultCount": 20
            }
            
            self.rate_limiter.wait_if_needed()
            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            competitors = []
            
            # Filter out the original business and parse competitors
            for place in data.get('places', []):
                if place.get('name') != business_name:
                    competitor = self._parse_business_data(place)
                    competitors.append(competitor)
            
            return competitors[:10]  # Return top 10 competitors
            
        except aiohttp.ClientError as e:
            logging.error(f"API request failed: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error getting competitors: {str(e)}")
            return []
        
    async def search_business(self, business_name: str, location: str = "Valencia, Spain") -> Optional[Dict[str, Any]]:
        """Search for a business by name and location."""
        self.rate_limiter.wait_if_needed()
        
        search_url = f"{self.base_url}:searchText"
        payload = {
            "textQuery": f"{business_name} {location}",
            "languageCode": "en"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            if not data.get("places"):
                logging.warning(f"No places found for query: {business_name} in {location}")
                return None
                
            return self._parse_business_data(data["places"][0])
            
        except aiohttp.ClientError as e:
            logging.error(f"API request failed: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error searching business: {str(e)}")
            return None
    
    async def get_reviews(self, place_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get reviews for a business."""
        self.rate_limiter.wait_if_needed()
        
        details_url = f"{self.base_url}/{place_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(details_url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            reviews = data.get("reviews", [])[:limit]
            return [self._parse_review(review) for review in reviews]
            
        except aiohttp.ClientError as e:
            logging.error(f"API request failed: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error fetching reviews: {str(e)}")
            return []
    
    def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse business data from API response."""
        try:
            return {
                'name': data.get('name', ''),
                'place_id': data.get('id', ''),
                'rating': data.get('rating', 0.0),
                'user_ratings_total': data.get('userRatingsTotal', 0),
                'price_level': data.get('priceLevel', 0),
                'formatted_address': data.get('formattedAddress', ''),
                'location': {
                    'latitude': data.get('location', {}).get('latitude', 0),
                    'longitude': data.get('location', {}).get('longitude', 0)
                },
                'opening_hours': {
                    'periods': data.get('currentOpeningHours', {}).get('periods', []),
                    'weekday_text': data.get('currentOpeningHours', {}).get('weekdayDescriptions', [])
                }
            }
        except Exception as e:
            logging.error(f"Error parsing business data: {str(e)}")
            return {}

    def _parse_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """Parse review data from API response."""
        try:
            return {
                'author_name': review.get('authorName', ''),
                'rating': review.get('rating', 0),
                'text': review.get('text', ''),
                'time': review.get('publishTime', ''),
                'language': review.get('languageCode', 'en')
            }
        except Exception as e:
            logging.error(f"Error parsing review: {str(e)}")
            return {}

    def _log_api_usage(self, operation: str, duration: float):
        """Log API usage for monitoring."""
        logging.info(f"Google Places API {operation} operation completed in {duration:.2f}s")
