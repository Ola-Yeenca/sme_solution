"""Restaurant-specific implementation of the business data fetcher."""

from typing import Dict, List, Any
from config.business_types import BusinessType
from shared.business_data_fetcher import BusinessDataFetcher
import random

class RestaurantDataFetcher(BusinessDataFetcher):
    """Data fetcher for restaurants."""

    def __init__(self, business_type: BusinessType):
        """Initialize with business type."""
        super().__init__(business_type)
        self.location_id = "187529"  # Valencia, Spain
        self.currency = "EUR"
        self.language = "en"
    
    def _get_search_params(self, business_name: str, location_id: str = None) -> Dict[str, str]:
        """Get parameters for restaurant search."""
        return {
            "locationId": location_id or self.location_id,
            "searchQuery": business_name,
            "language": self.language,
            "currency": self.currency
        }
    
    def _get_search_endpoint(self) -> str:
        """Get the search endpoint URL."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants"
    
    def _get_details_endpoint(self) -> str:
        """Get the details endpoint URL."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/{location_id}/details"
    
    def _get_competitor_search_params(self, location_id: str = None) -> Dict[str, str]:
        """Get parameters for competitor search."""
        return {
            "locationId": location_id or self.location_id,
            "page": "1",
            "currencyCode": self.currency,
            "language": self.language
        }
    
    def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse restaurant data from API response."""
        if not data.get('status', False):
            raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")

        restaurants = data.get('data', {}).get('data', [])
        if not restaurants:
            raise ValueError(f"No restaurants found")

        restaurant = restaurants[0]
        return {
            'name': restaurant.get('name', ''),
            'rating': restaurant.get('rating', 0.0),
            'reviews_count': restaurant.get('reviewsCount', 0),
            'price_level': restaurant.get('priceTag', '€€'),
            'cuisine': restaurant.get('establishmentTypeAndCuisineTags', []),
            'location': {
                'address': restaurant.get('address', ''),
                'latitude': restaurant.get('latitude', 0),
                'longitude': restaurant.get('longitude', 0)
            }
        }
    
    def _parse_competitor_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse competitor data from API response."""
        if not data.get('status', False):
            raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")

        restaurants = data.get('data', {}).get('data', [])
        competitors = []

        for restaurant in restaurants[1:6]:  # Skip first one (target business) and get next 5
            competitor = {
                'name': restaurant.get('name', ''),
                'rating': restaurant.get('rating', 0.0),
                'reviews_count': restaurant.get('reviewsCount', 0),
                'price_level': restaurant.get('priceTag', '€€'),
                'cuisine': restaurant.get('establishmentTypeAndCuisineTags', []),
                'distance_km': restaurant.get('distance', 0) / 1000  # Convert meters to kilometers
            }
            competitors.append(competitor)

        return competitors
    
    def _parse_review_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse review data from API response."""
        reviews = []
        review_data = data.get('data', {}).get('reviewList', {}).get('reviews', [])
        
        for review in review_data:
            reviews.append({
                'text': review.get('text', 'No review text available'),
                'rating': review.get('rating', 0),
                'date': review.get('publishedDate', ''),
                'title': review.get('title', ''),
                'is_recent': True  # Consider all fetched reviews as recent for now
            })
        
        return reviews

    def get_historical_data(self, business_name: str, months: int = 12) -> Dict[str, Any]:
        """Get historical sales and performance data."""
        try:
            # Get business details first
            business_data = self.get_business_details(business_name)
            
            # For now, generate simulated historical data since we don't have real historical data
            # This will be replaced with real API data when available
            monthly_data = []
            base_revenue = 10000  # Base monthly revenue
            seasonal_factors = [
                0.8,  # January
                0.9,  # February
                1.0,  # March
                1.1,  # April
                1.2,  # May
                1.3,  # June
                1.4,  # July
                1.5,  # August
                1.3,  # September
                1.1,  # October
                0.9,  # November
                1.0   # December
            ]
            
            for i in range(months):
                month_index = (12 - months + i) % 12
                seasonal_factor = seasonal_factors[month_index]
                
                # Add some random variation
                variation = random.uniform(0.9, 1.1)
                revenue = base_revenue * seasonal_factor * variation
                
                monthly_data.append({
                    'month': month_index + 1,
                    'revenue': round(revenue, 2),
                    'customers': round(revenue / 25),  # Average ticket size of 25
                    'avg_rating': round(min(5.0, business_data['rating'] + random.uniform(-0.3, 0.3)), 1)
                })
            
            return {
                'business_name': business_name,
                'total_months': months,
                'monthly_data': monthly_data,
                'avg_monthly_revenue': sum(m['revenue'] for m in monthly_data) / len(monthly_data),
                'avg_monthly_customers': sum(m['customers'] for m in monthly_data) / len(monthly_data),
                'trend': {
                    'revenue_growth': round((monthly_data[-1]['revenue'] / monthly_data[0]['revenue'] - 1) * 100, 1),
                    'customer_growth': round((monthly_data[-1]['customers'] / monthly_data[0]['customers'] - 1) * 100, 1)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error fetching historical data: {str(e)}")
