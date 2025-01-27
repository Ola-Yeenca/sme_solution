"""Hotel-specific implementation of the business data fetcher."""

from typing import Dict, List, Any

from shared.business_data_fetcher import BusinessDataFetcher
from config.business_types import BusinessType, DEFAULT_VALUES

class HotelDataFetcher(BusinessDataFetcher):
    def __init__(self, business_type: BusinessType):
        super().__init__(business_type)
        self.location_id = "187529"  # Valencia, Spain
        self.currency = "EUR"
        self.language = "en"
    
    def _get_search_params(self, business_name: str, location_id: str = None) -> Dict[str, str]:
        """Get parameters for hotel search."""
        return {
            "locationId": location_id or self.location_id,
            "searchQuery": business_name,
            "language": self.language,
            "currency": self.currency
        }
    
    def _get_search_endpoint(self) -> str:
        """Get the search endpoint URL."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels"
    
    def _get_details_endpoint(self) -> str:
        """Get the details endpoint URL."""
        return "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/{location_id}/details"
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse hotel-specific response."""
        try:
            return {
                "name": response.get("name", "Unknown"),
                "rating": response.get("rating", DEFAULT_VALUES["rating"]),
                "reviews_count": response.get("num_reviews", DEFAULT_VALUES["reviews_count"]),
                "price_level": response.get("price_level", DEFAULT_VALUES["price_level"]),
                "location": {
                    "latitude": response.get("latitude", DEFAULT_VALUES["latitude"]),
                    "longitude": response.get("longitude", DEFAULT_VALUES["longitude"]),
                    "address": response.get("address", "No address available")
                },
                "amenities": response.get("amenities", []),
                "room_types": response.get("room_types", []),
                "price_range": self.estimate_price_range(response.get("price_level", "€€€"))
            }
        except Exception as e:
            print(f"Error parsing hotel response: {str(e)}")
            return {
                "error": "Could not parse hotel data",
                "name": response.get("name", "Unknown")
            }
