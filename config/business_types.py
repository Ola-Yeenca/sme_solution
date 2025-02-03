"""Configuration for different business types and their API endpoints."""

from enum import Enum

class BusinessType(Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    ATTRACTION = "attraction"
    RETAIL = "retail"
    SERVICE = "service"

# API endpoints for different business types
API_ENDPOINTS = {
    BusinessType.RESTAURANT: {
        "search": "restaurant/searchRestaurants",
        "details": "restaurant/{location_id}/details",
        "reviews": "restaurant/{location_id}/reviews"
    },
    BusinessType.HOTEL: {
        "search": "hotels/searchHotels",
        "details": "hotels/{location_id}/details",
        "reviews": "hotels/{location_id}/reviews"
    },
    BusinessType.ATTRACTION: {
        "search": "attractions/searchAttractions",
        "details": "attractions/{location_id}/details",
        "reviews": "attractions/{location_id}/reviews"
    },
}

# Price configurations for different business types
PRICE_CONFIGS = {
    BusinessType.RESTAURANT: {
        "min_price": 10,
        "max_price": 200,
        "price_levels": ["€", "€€", "€€€", "€€€€"]
    },
    BusinessType.HOTEL: {
        "min_price": 50,
        "max_price": 500,
        "price_levels": ["€", "€€", "€€€", "€€€€"]
    },
    BusinessType.ATTRACTION: {
        "min_price": 5,
        "max_price": 100,
        "price_levels": ["€", "€€", "€€€"]
    },
}

# Analysis configurations for different business types
ANALYSIS_CONFIGS = {
    "sentiment": {
        "min_reviews": 5,
        "recent_threshold_days": 90
    },
    "pricing": {
        "competitor_radius_km": 2,
        "min_competitors": 3
    },
    "competitors": {
        "radius_km": 5,
        "max_competitors": 10
    }
}

# Default values for missing data
DEFAULT_VALUES = {
    "location_id": "187529",  # Valencia, Spain
    "currency": "EUR",
    "language": "en"
}
