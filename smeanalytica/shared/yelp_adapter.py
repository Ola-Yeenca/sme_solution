"""Yelp API adapter for fetching business data."""

import os
import logging
from typing import Dict, Any, List, Optional
import requests
import time
from datetime import datetime, timedelta
from ..config.data_sources import DataSourceConfig
from ..core.data.cache import DataCache

logger = logging.getLogger(__name__)

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

class YelpAdapter:
    """Adapter for Yelp Fusion API integration."""
    
    def __init__(self):
        """Initialize the Yelp adapter."""
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY environment variable is not set")
            
        self.base_url = "https://yelp-api-v3.p.rapidapi.com/v3"
        self.cache = DataCache()
        self.cache_duration = timedelta(hours=24)
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "yelp-api-v3.p.rapidapi.com",
            "Accept": "application/json"
        }
        
        # Initialize rate limiter (Yelp allows 5000 calls/day = ~3.5 calls/minute)
        self.rate_limiter = APIRateLimiter(DataSourceConfig.RATE_LIMITS.get('yelp', 3))
        
    async def get_complete_data(self, business_name: str, location: str = "Valencia, Spain") -> Dict[str, Any]:
        """Get complete business data including details and reviews.
        
        Args:
            business_name: Name of the business
            location: Location to search in
            
        Returns:
            Dictionary containing all available business data
        """
        start_time = time.time()
        try:
            # Search for the business first
            business_data = await self.search_business(business_name, location)
            if not business_data:
                return None
            
            # Get business ID
            business_id = business_data.get('id')
            if not business_id:
                return business_data
            
            # Get reviews
            reviews = await self.get_reviews(business_id)
            business_data['reviews'] = reviews
            
            self._log_api_usage('get_complete_data', time.time() - start_time)
            return business_data
            
        except Exception as e:
            logger.error(f"Error getting complete Yelp data: {str(e)}")
            return None
    
    async def search_business(self, business_name: str, location: str = "Valencia, Spain") -> Optional[Dict[str, Any]]:
        """Search for a business by name and location."""
        self.rate_limiter.wait_if_needed()
        
        try:
            params = {
                'term': business_name,
                'location': location,
                'limit': 1,  # Get best match only
                'sort_by': 'best_match'
            }
            
            response = requests.get(
                f"{self.base_url}/businesses/search",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            businesses = data.get('businesses', [])
            
            if not businesses:
                return None
                
            return self._parse_business_data(businesses[0])
            
        except Exception as e:
            logger.error(f"Error searching Yelp business: {str(e)}")
            return None
    
    async def get_reviews(self, business_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get reviews for a business."""
        self.rate_limiter.wait_if_needed()
        
        try:
            params = {'limit': min(limit, 50)}  # Yelp max is 50
            response = requests.get(
                f"{self.base_url}/businesses/{business_id}/reviews",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            reviews = data.get('reviews', [])
            
            return [self._parse_review(review) for review in reviews]
            
        except Exception as e:
            logger.error(f"Error getting Yelp reviews: {str(e)}")
            return []
    
    def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse business data from API response."""
        return {
            'source': 'yelp',
            'id': data.get('id'),
            'name': data.get('name'),
            'rating': data.get('rating'),
            'review_count': data.get('review_count'),
            'price_level': len(data.get('price', '$')) if data.get('price') else None,
            'categories': [cat['title'] for cat in data.get('categories', [])],
            'address': data.get('location', {}).get('address1'),
            'city': data.get('location', {}).get('city'),
            'state': data.get('location', {}).get('state'),
            'zip_code': data.get('location', {}).get('zip_code'),
            'country': data.get('location', {}).get('country'),
            'phone': data.get('phone'),
            'url': data.get('url'),
            'photos': data.get('photos', []),
            'coordinates': {
                'latitude': data.get('coordinates', {}).get('latitude'),
                'longitude': data.get('coordinates', {}).get('longitude')
            },
            'hours': data.get('hours', [{}])[0].get('open', []) if data.get('hours') else None,
            'is_closed': data.get('is_closed', False),
            'transactions': data.get('transactions', []),
            'attributes': data.get('attributes', {})
        }
    
    def _parse_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """Parse review data from API response."""
        return {
            'id': review.get('id'),
            'rating': review.get('rating'),
            'text': review.get('text'),
            'time_created': review.get('time_created'),
            'user': {
                'id': review.get('user', {}).get('id'),
                'name': review.get('user', {}).get('name'),
                'profile_url': review.get('user', {}).get('profile_url')
            }
        }
    
    def _log_api_usage(self, operation: str, duration: float):
        """Log API usage for monitoring."""
        logger.info(f"Yelp API {operation} completed in {duration:.2f}s")
