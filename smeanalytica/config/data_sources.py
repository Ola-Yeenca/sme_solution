"""Configuration for data sources and their priorities."""

from enum import Enum
from typing import List, Dict

class DataSourcePriority(Enum):
    """Priority order for different data types."""
    BUSINESS_INFO = ['google_places', 'yelp', 'tripadvisor']
    COMPETITORS = ['google_places', 'yelp', 'tripadvisor']
    REVIEWS = ['google_places', 'yelp', 'tripadvisor']
    HISTORICAL_DATA = ['yelp', 'tripadvisor']

class DataSourceConfig:
    """Configuration for data source behavior."""
    
    # Minimum requirements for complete data
    MINIMUM_REQUIREMENTS = {
        'business_info': ['name', 'rating', 'price_level'],
        'competitors': ['name', 'rating', 'price_level'],
        'reviews': ['text', 'rating', 'date']
    }
    
    # Preferred fields from each source
    PREFERRED_FIELDS = {
        'google_places': ['name', 'rating', 'total_ratings', 'price_level', 'location'],
        'yelp': ['name', 'rating', 'review_count', 'price_level', 'categories', 'transactions', 'attributes'],
        'tripadvisor': ['name', 'rating', 'reviews_count', 'price_level', 'cuisine']
    }
    
    # Cost weights for different operations (arbitrary units)
    COST_WEIGHTS = {
        'google_places': {
            'business_info': 1,
            'competitors': 1,
            'reviews': 1
        },
        'yelp': {
            'search': 1,
            'details': 2,
            'reviews': 2
        },
        'tripadvisor': {
            'business_info': 5,
            'competitors': 5,
            'reviews': 5
        }
    }
    
    # Rate limits (requests per minute)
    RATE_LIMITS = {
        'google_places': 500,  # Google Places API standard limit
        'yelp': 3,  # ~5000/day = ~3.5/minute
        'tripadvisor': 30      # TripAdvisor API standard limit
    }
    
    # Cache durations in hours
    CACHE_DURATIONS = {
        'google_places': 24,
        'yelp': 24,
        'tripadvisor': 24
    }
    
    @classmethod
    def is_data_sufficient(cls, data_type: str, data: Dict) -> bool:
        """Check if data meets minimum requirements."""
        if not data:
            return False
            
        required_fields = cls.MINIMUM_REQUIREMENTS.get(data_type, [])
        
        # For business info, we want at least 2/3 of the required fields
        if data_type == 'business_info':
            present_fields = sum(1 for field in required_fields if field in data and data[field])
            return present_fields >= len(required_fields) * 2/3
            
        # For other types, we want all required fields
        return all(field in data and data[field] for field in required_fields)
        
    @classmethod
    def get_preferred_fields(cls, source: str) -> List[str]:
        """Get preferred fields for a given source."""
        return cls.PREFERRED_FIELDS.get(source, [])
