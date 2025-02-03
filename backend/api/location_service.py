from typing import Dict, Any
import requests
from flask import current_app
import json
from pathlib import Path
import os

class LocationService:
    def __init__(self):
        self.cache_dir = Path("cache/location_data")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_location_stats(self, city: str) -> Dict[str, Any]:
        """Get business statistics for a specific city."""
        # Try to get from cache first
        cache_file = self.cache_dir / f"{city.lower()}_stats.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # If not in cache, fetch from external APIs
        try:
            # Get business data from Google Places API
            places_data = self._fetch_places_data(city)
            
            # Get demographic data
            demographic_data = self._fetch_demographic_data(city)
            
            # Combine and process the data
            stats = self._process_location_data(places_data, demographic_data)
            
            # Cache the results
            with open(cache_file, 'w') as f:
                json.dump(stats, f)
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Error fetching stats for {city}: {str(e)}")
            # Return default stats if there's an error
            return self._get_default_stats()
    
    def _fetch_places_data(self, city: str) -> Dict[str, Any]:
        """Fetch business data from Google Places API."""
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not api_key:
            raise ValueError("Google Places API key not configured")
            
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': f'businesses in {city}',
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _fetch_demographic_data(self, city: str) -> Dict[str, Any]:
        """Fetch demographic data for the city."""
        # This could be integrated with a demographics API service
        # For now, return mock data
        return {
            'population': 500000,
            'median_income': 55000,
            'business_growth_rate': 0.05
        }
    
    def _process_location_data(self, places_data: Dict[str, Any], demographic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and combine data from different sources."""
        total_businesses = len(places_data.get('results', []))
        
        return {
            'stats': {
                'total_businesses': total_businesses,
                'market_size': f"${demographic_data['population'] * demographic_data['median_income'] / 1000000:.1f}M",
                'growth_rate': f"{demographic_data['business_growth_rate'] * 100:.1f}%",
                'business_density': f"{total_businesses / (demographic_data['population'] / 100000):.0f}"
            }
        }
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """Return default stats when actual data cannot be fetched."""
        return {
            'stats': {
                'total_businesses': '1000+',
                'market_size': '$500M+',
                'growth_rate': '5.0%',
                'business_density': '200'
            }
        }
