"""Attraction-specific implementation of the business data fetcher."""

from typing import Dict, List, Any

from shared.business_data_fetcher import BusinessDataFetcher
from config.business_types import BusinessType

class AttractionDataFetcher(BusinessDataFetcher):
    def __init__(self, business_type: BusinessType):
        super().__init__(business_type)
        self.location_id = "187529"  # Valencia, Spain
        self.currency = "EUR"
        self.language = "en"
    
    def _get_search_params(self, business_name: str, location_id: str = None) -> Dict[str, str]:
        """Get parameters for attraction search."""
        return {
            "locationId": location_id or self.location_id,
            "searchQuery": business_name,
            "language": self.language,
            "currency": self.currency
        }
    
    def _get_competitor_search_params(self, location_id: str = None) -> Dict[str, str]:
        """Get parameters for competitor search."""
        return {
            "locationId": location_id or self.location_id,
            "page": "1",
            "currencyCode": self.currency,
            "language": self.language,
            "category": "all" 
        }
    
    def _parse_business_data(self, data: Dict, business_name: str) -> Dict[str, Any]:
        """Parse attraction data from API response."""
        attractions = data.get('data', {}).get('data', [])
        if not attractions:
            return self._get_default_response(business_name)
        
        
        target_attraction = None
        for attraction in attractions:
            attraction_name = attraction['name'].lower()
            search_name = business_name.lower()
            
            if (attraction_name == search_name or
                search_name in attraction_name or
                attraction_name in search_name):
                target_attraction = attraction
                break
        
        if not target_attraction and attractions:
            target_attraction = attractions[0]
            print(f"No exact match found. Using closest match: {target_attraction['name']}")
        
        if target_attraction:
            price_tag = target_attraction.get('priceTag', '$$')
            price_range = self.estimate_price_range(price_tag)
            
            return {
                'name': target_attraction['name'],
                'location_id': target_attraction['locationId'],
                'rating': target_attraction.get('averageRating', 0.0),
                'reviews_count': target_attraction.get('userReviewCount', 0),
                'price_level': price_tag,
                'price_range': price_range,
                'category': target_attraction.get('category', []),
                'duration': target_attraction.get('suggestedDuration', ''),
                'address': target_attraction.get('address', ''),
                'phone': target_attraction.get('phone', ''),
                'website': target_attraction.get('website', ''),
                'booking_info': target_attraction.get('bookingInfo', {}),
                'review_snippets': [
                    review.get('reviewText', '')
                    for review in target_attraction.get('reviewSnippets', {}).get('reviewSnippetsList', [])
                ]
            }
        
        return self._get_default_response(business_name)
    
    def _parse_competitor_data(self, data: Dict, business_name: str) -> List[Dict[str, Any]]:
        """Parse competitor data from API response."""
        attractions = data.get('data', {}).get('data', [])
        target_attraction = None
        competitors = []
        
        
        for attraction in attractions:
            if attraction['name'].lower() == business_name.lower():
                target_attraction = attraction
                break
        
        target_category = target_attraction.get('category', []) if target_attraction else []
        
        
        for attraction in attractions[:20]:
            if attraction['name'].lower() != business_name.lower():
                attraction_category = attraction.get('category', [])
                if not target_category or any(cat in target_category for cat in attraction_category):
                    price_tag = attraction.get('priceTag', '$$')
                    price_range = self.estimate_price_range(price_tag)
                    
                    competitors.append({
                        'name': attraction['name'],
                        'price_range': price_range,
                        'rating': attraction.get('averageRating', 0.0),
                        'reviews_count': attraction.get('userReviewCount', 0),
                        'price_level': price_tag,
                        'category': attraction_category,
                        'duration': attraction.get('suggestedDuration', '')
                    })
        
        
        competitors.sort(key=lambda x: (x['rating'], x['reviews_count']), reverse=True)
        return competitors[:10]
    
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
                'is_recent': True,      
                'visit_type': review.get('visitType', ''),
                'visit_date': review.get('visitDate', '')
            })
        
        return reviews
    
    def _get_search_endpoint(self) -> str:
        """Get the search endpoint URL."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/attractions/searchAttractions"
    
    def _get_details_endpoint(self) -> str:
        """Get the details endpoint URL."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/attractions/{location_id}/details"
