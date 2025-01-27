"""Base class for fetching business data."""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import random

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

from config.business_types import BusinessType, PRICE_CONFIGS, API_ENDPOINTS, ANALYSIS_CONFIGS, DEFAULT_VALUES

class BusinessDataFetcher(ABC):
    """Abstract base class for business data fetchers."""

    def __init__(self, business_type: BusinessType):
        """Initialize the business data fetcher."""
        # Load environment variables
        load_dotenv()
        
        self.business_type = business_type
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY environment variable is not set")
        
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com",
            "Content-Type": "application/json"
        }

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
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Rate limiting with jitter
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Increase minimum interval between requests
        self.jitter_range = 0.5  # Add random jitter to avoid synchronized requests
    
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
    
    def get_business_details(self, business_name: str) -> Dict[str, Any]:
        """Get business details from the API."""
        try:
            url = self._get_search_endpoint()
            params = self._get_search_params(business_name)
            
            response = self._make_api_request(url, params)
            if not response:
                raise Exception("No response received from API")
            
            return self._parse_business_data(response)
            
        except Exception as e:
            raise Exception(f"Error fetching business details: {str(e)}")
    
    def get_competitors(self, business_name: str) -> List[Dict[str, Any]]:
        """Get competitors near the business location."""
        try:
            url = self._get_search_endpoint()
            params = self._get_search_params(business_name)
            
            response = self._make_api_request(url, params)
            if not response:
                raise Exception("No response received from API")
            
            return self._parse_competitor_data(response)
            
        except Exception as e:
            raise Exception(f"Error fetching competitors: {str(e)}")
    
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
                response = self.session.get(url, headers=self.headers, params=params)
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
                    
                    app.logger.warning(f"Rate limit hit, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    current_retry += 1
                    continue
                else:
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                if current_retry < max_retries - 1:
                    wait_time = base_wait_time * (2 ** current_retry) + random.uniform(0, 2)
                    app.logger.warning(f"Request failed, retrying in {wait_time} seconds")
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
