"""Google Places API adapter for business data fetching."""

import os
import time
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime, timedelta
import json
from config.data_sources import DataSourceConfig

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
            raise ValueError("GOOGLE_PLACES_API_KEY environment variable is not set")
        
        self.base_url = "https://places.googleapis.com/v1/places"
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "name,rating,userRatingsTotal,reviews,priceLevel,formattedAddress,currentOpeningHours,regularOpeningHours,location",
            "X-Goog-User-Project": "valencia-sme-solutions"
        }
        
        # Initialize rate limiter
        self.rate_limiter = APIRateLimiter(DataSourceConfig.RATE_LIMITS['google_places'])
        
    def get_complete_data(self, business_name: str, location: str = "Valencia, Spain") -> Dict[str, Any]:
        """Get complete business data including details and reviews.
        
        Args:
            business_name: Name of the business
            location: Location to search in
            
        Returns:
            Dictionary containing all available business data
        """
        start_time = time.time()
        try:
            # Get basic business data
            business_data = self.search_business(business_name, location)
            if not business_data:
                return {}
            
            # Get reviews if available
            if business_data.get('place_id'):
                reviews = self.get_reviews(business_data['place_id'])
                business_data['reviews'] = reviews
            
            return business_data
            
        finally:
            duration = time.time() - start_time
            self._log_api_usage('complete_data', duration)
    
    def search_business(self, business_name: str, location: str = "Valencia, Spain") -> Optional[Dict[str, Any]]:
        """Search for a business by name and location."""
        self.rate_limiter.wait_if_needed()
        
        search_url = f"{self.base_url}:searchText"
        payload = {
            "textQuery": f"{business_name} {location}",
            "languageCode": "en"
        }
        
        try:
            response = requests.post(search_url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("places"):
                return None
                
            return self._parse_business_data(data["places"][0])
            
        except Exception as e:
            print(f"Error searching business: {e}")
            return None
    
    def get_reviews(self, place_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get reviews for a business."""
        self.rate_limiter.wait_if_needed()
        
        details_url = f"{self.base_url}/{place_id}"
        
        try:
            response = requests.get(details_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            reviews = data.get("reviews", [])[:limit]
            
            return [self._parse_review(review) for review in reviews]
            
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return []
    
    def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse business data from API response."""
        return {
            "name": data.get("name", ""),
            "place_id": data.get("id", ""),
            "rating": float(data.get("rating", 0.0)),
            "total_ratings": int(data.get("userRatingsTotal", 0)),
            "price_level": data.get("priceLevel", ""),
            "address": data.get("formattedAddress", ""),
            "location": {
                "latitude": data.get("location", {}).get("latitude", 0),
                "longitude": data.get("location", {}).get("longitude", 0)
            },
            "source": "google_places"
        }
    
    def _parse_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """Parse review data from API response."""
        return {
            "rating": review.get("rating", 0),
            "text": review.get("text", ""),
            "time": review.get("publishTime", ""),
            "author": review.get("authorName", "Anonymous"),
            "language": review.get("languageCode", "en"),
            "source": "google_places"
        }
    
    def _log_api_usage(self, operation: str, duration: float):
        """Log API usage for monitoring."""
        print(f"Google Places API - {operation}: {duration:.2f}s")
