"""Base class for data fetchers."""

import os
import json
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from statistics import mean
from dotenv import load_dotenv
import asyncio
import aiohttp
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from smeanalytica.config.business_types import (
    BusinessType, PRICE_CONFIGS, API_ENDPOINTS, 
    ANALYSIS_CONFIGS, DEFAULT_VALUES
)

from smeanalytica.shared.google_places_adapter import GooglePlacesAdapter
from smeanalytica.shared.cache import DataCache
from smeanalytica.utils.performance import PerformanceMonitor

logger = logging.getLogger(__name__)
performance = PerformanceMonitor()

class BusinessDataFetcher(ABC):
    """Abstract base class for business data fetchers."""

    def __init__(self, business_type: BusinessType, cache_ttl: int = 3600):
        """Initialize the business data fetcher."""
        # Load environment variables
        load_dotenv()
        
        self.business_type = business_type
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if not self.rapidapi_key:
            raise ValueError("RAPIDAPI_KEY environment variable is not set")
            
        # Initialize data source adapters
        try:
            self.google_places = GooglePlacesAdapter()
            self.has_google_places = True
        except ValueError:
            print("Warning: Google Places API not configured, falling back to TripAdvisor only")
            self.has_google_places = False
            
        # Configure retry strategy with longer delays
        retry_strategy = Retry(
            total=5,  # Increase total retries
            backoff_factor=2,  # Increase backoff factor for longer waits
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True,  # Honor Retry-After headers
            raise_on_status=True
        )
        
        # Configure session
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Rate limiting with jitter
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Increase minimum interval between requests
        self.jitter_range = 0.5  # Add random jitter to avoid synchronized requests
        
        # Initialize cache
        self.cache = DataCache(cache_ttl)
        self.api_keys = {
            'google_places': os.getenv('GOOGLE_PLACES_API_KEY'),
            'rapidapi': os.getenv('RAPIDAPI_KEY'),
            'openrouter': os.getenv('OPENROUTER_API_KEY')
        }
        
        # Validate API keys
        missing_keys = [k for k, v in self.api_keys.items() if not v]
        if missing_keys:
            logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
    
    async def initialize(self):
        """Initialize cache and other async resources."""
        await self.cache.initialize()
        logger.info("BusinessDataFetcher initialized successfully")
        return self
    
    async def get_business_data(self, business_name: str) -> Dict[str, Any]:
        """Get comprehensive business data with caching."""
        if not self.cache:
            raise RuntimeError("BusinessDataFetcher not initialized. Call initialize() first.")
            
        cache_key = f"business_data_{business_name}"
        
        try:
            # Check cache first
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {business_name}")
                return cached_data
            
            with performance.measure(f"fetch_business_data_{business_name}"):
                # Fetch data from multiple sources concurrently
                tasks = [
                    self._fetch_google_places_data(business_name),
                    self._fetch_rapidapi_data(business_name),
                    self._fetch_additional_data(business_name)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Merge valid results
                business_data = {}
                for result in results:
                    if isinstance(result, dict):
                        business_data.update(result)
                
                if not business_data:
                    logger.error(f"No valid data found for {business_name}")
                    return {}
                
                # Cache the results
                await self.cache.set(cache_key, business_data)
                return business_data
                
        except Exception as e:
            logger.error(f"Error fetching business data for {business_name}: {str(e)}")
            return {}
    
    async def _fetch_google_places_data(self, business_name: str) -> Dict[str, Any]:
        """Fetch data from Google Places API."""
        if not self.api_keys['google_places']:
            return {}
            
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query': business_name,
                    'key': self.api_keys['google_places']
                }
                async with session.get(
                    'https://maps.googleapis.com/maps/api/place/textsearch/json',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('results'):
                            place = data['results'][0]
                            return {
                                'name': place.get('name'),
                                'rating': place.get('rating'),
                                'reviews_count': place.get('user_ratings_total'),
                                'price_level': '€' * (place.get('price_level', 2) + 1),
                                'address': place.get('formatted_address'),
                                'place_id': place.get('place_id')
                            }
            return {}
            
        except Exception as e:
            logger.error(f"Google Places API error: {str(e)}")
            return {}
    
    async def _fetch_rapidapi_data(self, business_name: str) -> Dict[str, Any]:
        """Fetch data from RapidAPI endpoints."""
        if not self.api_keys['rapidapi']:
            return {}
            
        try:
            headers = {
                'X-RapidAPI-Key': self.api_keys['rapidapi'],
                'X-RapidAPI-Host': 'local-business-data.p.rapidapi.com'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://local-business-data.p.rapidapi.com/search',
                    headers=headers,
                    params={'query': business_name, 'limit': 1}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data'):
                            business = data['data'][0]
                            return {
                                'categories': business.get('categories', []),
                                'hours': business.get('hours', {}),
                                'phone': business.get('phone'),
                                'website': business.get('website')
                            }
            return {}
            
        except Exception as e:
            logger.error(f"RapidAPI error: {str(e)}")
            return {}
    
    async def _fetch_additional_data(self, business_name: str) -> Dict[str, Any]:
        """Fetch additional business data from other sources."""
        # Simulate fetching additional data
        await asyncio.sleep(0.1)
        return {
            'last_updated': datetime.now().isoformat(),
            'data_sources': ['google_places', 'rapidapi', 'local_cache']
        }
    
    async def get_historical_data(self, business_name: str) -> Dict[str, Any]:
        """Get historical performance data."""
        # For testing, return simulated historical data
        return {
            'monthly_revenue': [
                50000, 48000, 52000, 55000, 60000, 65000,
                70000, 68000, 62000, 58000, 54000, 56000
            ],
            'customer_counts': [
                1200, 1150, 1300, 1400, 1500, 1600,
                1700, 1650, 1450, 1350, 1250, 1300
            ],
            'average_ratings': [
                4.2, 4.3, 4.2, 4.4, 4.5, 4.6,
                4.6, 4.5, 4.4, 4.3, 4.3, 4.4
            ]
        }
    
    async def get_competitors(self, business_name: str) -> List[Dict[str, Any]]:
        """Get competitor data."""
        # For testing, return simulated competitor data
        return [
            {
                'name': 'Competitor 1',
                'rating': 4.3,
                'reviews_count': 150,
                'price_level': '€€'
            },
            {
                'name': 'Competitor 2',
                'rating': 4.1,
                'reviews_count': 200,
                'price_level': '€€€'
            }
        ]
    
    def estimate_price_range(self, price_level: str) -> Tuple[float, float]:
        """Estimate price range based on price level."""
        try:
            price_config = PRICE_CONFIGS.get(self.business_type, {})
            min_price = price_config.get("min_price", 0)
            max_price = price_config.get("max_price", 100)
            price_levels = price_config.get("price_levels", ["€"])
            
            # Convert price level to index (e.g., "€€" -> 1)
            level_index = len(price_level) - 1
            total_levels = len(price_levels)
            
            # Calculate price range based on index
            range_size = (max_price - min_price) / total_levels
            range_min = min_price + (level_index * range_size)
            range_max = range_min + range_size
            
            return (range_min, range_max)
        except Exception as e:
            print(f"Error estimating price range: {str(e)}")
            return (0, 100)
    
    def get_business_data(self, business_name: str) -> Dict[str, Any]:
        """Get business data from available sources.
        
        Args:
            business_name: Name of the business to fetch data for
            
        Returns:
            Dictionary containing combined business data
        """
        data = {
            "tripadvisor": self._get_tripadvisor_data(business_name),
            "google_places": None
        }
        
        if self.has_google_places:
            google_data = self.google_places.search_business(business_name)
            if google_data:
                data["google_places"] = google_data
                
        return self._combine_business_data(data)
        
    def get_reviews(self, business_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get reviews from all available sources.
        
        Args:
            business_name: Name of the business to fetch reviews for
            limit: Maximum number of reviews per source
            
        Returns:
            List of review dictionaries from all sources
        """
        reviews = []
        
        # Get TripAdvisor reviews
        tripadvisor_data = self._get_tripadvisor_data(business_name)
        if tripadvisor_data and "reviews" in tripadvisor_data:
            reviews.extend(tripadvisor_data["reviews"][:limit])
            
        # Get Google Places reviews if available
        if self.has_google_places:
            google_data = self.google_places.search_business(business_name)
            if google_data:
                google_reviews = self.google_places.get_reviews(google_data["place_id"], limit)
                reviews.extend(google_reviews)
                
        return reviews
        
    def _combine_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine business data from multiple sources.
        
        Args:
            data: Dictionary containing data from different sources
            
        Returns:
            Dictionary containing combined business data
        """
        combined = {
            "name": "",
            "rating": 0.0,
            "total_ratings": 0,
            "price_level": "",
            "address": "",
            "reviews": [],
            "sources": []
        }
        
        # Process TripAdvisor data
        if data["tripadvisor"]:
            combined["sources"].append("tripadvisor")
            ta_data = data["tripadvisor"]
            combined.update({
                "name": ta_data.get("name", combined["name"]),
                "rating": float(ta_data.get("rating", 0)),
                "total_ratings": int(ta_data.get("num_reviews", 0)),
                "price_level": ta_data.get("price_level", ""),
                "address": ta_data.get("address", ""),
                "reviews": ta_data.get("reviews", [])
            })
            
        # Process Google Places data
        if data["google_places"]:
            combined["sources"].append("google_places")
            gp_data = data["google_places"]
            
            # Update with Google data or keep existing if Google data is missing
            if not combined["name"]:
                combined["name"] = gp_data.get("name", "")
            if not combined["rating"]:
                combined["rating"] = float(gp_data.get("rating", 0))
            if not combined["total_ratings"]:
                combined["total_ratings"] = int(gp_data.get("total_ratings", 0))
            if not combined["price_level"]:
                combined["price_level"] = gp_data.get("price_level", "")
            if not combined["address"]:
                combined["address"] = gp_data.get("address", "")
                
            combined["reviews"].extend(gp_data.get("reviews", []))
            
        return combined
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
    def _get_tripadvisor_data(self, business_name: str) -> Dict[str, Any]:
        """Get TripAdvisor data for the business."""
        url = self._get_search_endpoint()
        params = self._get_search_params(business_name)
        
        response = self._make_api_request(url, params)
        if not response:
            raise Exception("No response received from API")
        
        return self._parse_business_data(response)
    
    def _make_api_request(self, url: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make an API request with improved rate limiting and retry logic."""
        max_retries = 3
        current_retry = 0
        base_wait_time = 5  # Base wait time in seconds

        while current_retry < max_retries:
            try:
                # Add jitter to rate limiting
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                jitter = random.uniform(0, self.jitter_range)
                
                if time_since_last_request < self.min_request_interval:
                    wait_time = self.min_request_interval - time_since_last_request + jitter
                    time.sleep(wait_time)

                # Make the request
                response = self.session.get(url, headers=self._get_headers(), params=params)
                self.last_request_time = time.time()

                # Handle different response status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Get retry after time, default to exponential backoff
                    retry_after = int(response.headers.get('Retry-After', 
                        base_wait_time * (2 ** current_retry)))
                    
                    # Add jitter to retry time
                    retry_after += random.uniform(0, 2)
                    
                    print(f"Rate limit hit, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    current_retry += 1
                    continue
                else:
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                if current_retry < max_retries - 1:
                    wait_time = base_wait_time * (2 ** current_retry) + random.uniform(0, 2)
                    print(f"Request failed, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    current_retry += 1
                    continue
                else:
                    if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                        raise Exception(
                            "API rate limit exceeded. Please try again in a few minutes."
                        )
                    else:
                        raise Exception(f"API request failed after {max_retries} retries: {str(e)}")

        raise Exception("Max retries exceeded, please try again later")
    
    @abstractmethod
    def _get_search_params(self, business_name: str) -> Dict[str, Any]:
        """Get search parameters for the business type."""
        pass
    
    @abstractmethod
    def _get_search_endpoint(self) -> str:
        """Get the search endpoint URL."""
        pass
    
    @abstractmethod
    def _get_details_endpoint(self) -> str:
        """Get the details endpoint URL."""
        pass
    
    @abstractmethod
    def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse business data from API response."""
        pass
    
    @abstractmethod
    def _parse_competitor_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse competitor data from API response."""
        pass
