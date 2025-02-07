"""Mock data fetcher for testing."""

from typing import Dict, Any, List
from datetime import datetime

from smeanalytica.shared.business_data_fetcher import BusinessDataFetcher
from smeanalytica.types.business_type import BusinessType

class MockDataFetcher(BusinessDataFetcher):
    """Mock data fetcher that returns predefined test data."""
    
    def __init__(self, business_type: BusinessType = BusinessType.RESTAURANT, cache_ttl: int = 3600):
        """Initialize mock data fetcher."""
        super().__init__(business_type, cache_ttl)
        self.mock_data = {
            'La Riua': {
                'name': 'La Riua',
                'rating': 4.5,
                'reviews_count': 250,
                'price_level': '€€',
                'address': '123 Test St, Test City',
                'place_id': 'test_place_id_1',
                'categories': ['Restaurant', 'Spanish', 'Mediterranean'],
                'hours': {
                    'Monday': '11:00-23:00',
                    'Tuesday': '11:00-23:00',
                    'Wednesday': '11:00-23:00',
                    'Thursday': '11:00-23:00',
                    'Friday': '11:00-00:00',
                    'Saturday': '11:00-00:00',
                    'Sunday': '11:00-23:00'
                },
                'phone': '+1234567890',
                'website': 'http://lariua.test'
            },
            'Grand Hotel': {
                'name': 'Grand Hotel',
                'rating': 4.3,
                'reviews_count': 500,
                'price_level': '€€€',
                'address': '456 Luxury Ave, Test City',
                'place_id': 'test_place_id_2',
                'categories': ['Hotel', 'Luxury', 'Spa'],
                'hours': {
                    'Monday': '00:00-23:59',
                    'Tuesday': '00:00-23:59',
                    'Wednesday': '00:00-23:59',
                    'Thursday': '00:00-23:59',
                    'Friday': '00:00-23:59',
                    'Saturday': '00:00-23:59',
                    'Sunday': '00:00-23:59'
                },
                'phone': '+0987654321',
                'website': 'http://grandhotel.test',
                'amenities': ['Pool', 'Spa', 'Restaurant', 'Room Service']
            },
            'Fashion Boutique': {
                'name': 'Fashion Boutique',
                'rating': 4.0,
                'reviews_count': 120,
                'price_level': '€€',
                'address': '789 Fashion St, Test City',
                'place_id': 'test_place_id_3',
                'categories': ['Retail', 'Fashion', 'Clothing'],
                'hours': {
                    'Monday': '10:00-20:00',
                    'Tuesday': '10:00-20:00',
                    'Wednesday': '10:00-20:00',
                    'Thursday': '10:00-20:00',
                    'Friday': '10:00-21:00',
                    'Saturday': '10:00-21:00',
                    'Sunday': '11:00-19:00'
                },
                'phone': '+1122334455',
                'website': 'http://fashionboutique.test',
                'specialties': ['Designer Clothing', 'Accessories', 'Custom Tailoring']
            }
        }
        
    async def get_business_details(self, business_name: str) -> Dict[str, Any]:
        """Get mock business details."""
        return self.mock_data.get(business_name, {})
        
    async def _get_search_endpoint(self) -> str:
        """Get mock search endpoint."""
        return 'https://mock.api/search'
        
    async def _get_details_endpoint(self) -> str:
        """Get mock details endpoint."""
        return 'https://mock.api/details'
        
    async def _get_search_params(self, query: str) -> Dict[str, Any]:
        """Get mock search parameters."""
        return {'query': query}
        
    async def _parse_business_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse mock business data."""
        if not data:
            return {}
            
        return {
            'name': data.get('name', ''),
            'rating': data.get('rating', 0.0),
            'reviews_count': data.get('reviews_count', 0),
            'price_level': data.get('price_level', '€'),
            'address': data.get('address', ''),
            'place_id': data.get('place_id', ''),
            'categories': data.get('categories', []),
            'hours': data.get('hours', {}),
            'phone': data.get('phone', ''),
            'website': data.get('website', '')
        }
        
    async def _parse_competitor_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse mock competitor data."""
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
        
    async def get_business_data(self, business_name: str) -> Dict[str, Any]:
        """Get mock business data."""
        if business_name in self.mock_data:
            return self.mock_data[business_name]
        return {}
