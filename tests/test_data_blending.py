"""Test suite for data blending implementation."""

import unittest
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from config.business_types import BusinessType
from shared.restaurant_data_fetcher import RestaurantDataFetcher

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestDataBlending(unittest.TestCase):
    """Test cases for data blending implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.fetcher = RestaurantDataFetcher(BusinessType.RESTAURANT)
        self.test_business = "La Riua"
    
    @patch('shared.google_places_adapter.GooglePlacesAdapter.get_complete_data')
    @patch('shared.restaurant_data_fetcher.RestaurantDataFetcher._get_tripadvisor_data')
    def test_business_data_blending(self, mock_ta, mock_google):
        """Test business data blending strategy."""
        # Mock Google Places data
        google_data = {
            'name': 'La Riua',
            'rating': 4.5,
            'total_ratings': 100,
            'price_level': '€€'
        }
        mock_google.return_value = google_data.copy()
        logger.debug(f"Initial Google mock data: {google_data}")
        
        # Mock TripAdvisor data
        ta_data = {
            'name': 'La Riua',
            'rating': 4.3,
            'reviews_count': 150,
            'price_level': '€€-€€€',
            'cuisine': ['Spanish', 'Mediterranean'],
            'source': 'tripadvisor'
        }
        mock_ta.return_value = ta_data.copy()
        logger.debug(f"Initial TripAdvisor mock data: {ta_data}")
        
        # Test complete Google data
        logger.debug("Testing complete Google data...")
        data = self.fetcher.get_business_data(self.test_business)
        logger.debug(f"Received data from complete Google test: {data}")
        self.assertEqual(data.get('source'), 'google_places')
        self.assertEqual(data.get('rating'), 4.5)
        
        # Test blending when Google data is incomplete
        logger.debug("Testing incomplete Google data...")
        incomplete_google = {'name': 'La Riua', 'source': 'google_places'}
        mock_google.return_value = incomplete_google.copy()
        logger.debug(f"Setting incomplete Google data: {incomplete_google}")
        
        data = self.fetcher.get_business_data(self.test_business)
        logger.debug(f"Received data from incomplete Google test: {data}")
        logger.debug(f"Mock calls - Google: {mock_google.call_count}, TripAdvisor: {mock_ta.call_count}")
        
        self.assertTrue('cuisine' in data, "Blended data should include TripAdvisor cuisine data")
        self.assertEqual(data.get('source'), 'tripadvisor')
        self.assertEqual(data.get('cuisine'), ['Spanish', 'Mediterranean'])
        self.assertEqual(data.get('price_level'), '€€-€€€')
    
    @patch('shared.google_places_adapter.GooglePlacesAdapter.search_business')
    @patch('shared.google_places_adapter.GooglePlacesAdapter.get_reviews')
    @patch('shared.restaurant_data_fetcher.RestaurantDataFetcher._get_tripadvisor_reviews')
    def test_review_blending(self, mock_ta_reviews, mock_google_reviews, mock_google_search):
        """Test review blending strategy."""
        # Mock Google Places business search
        mock_google_search.return_value = {
            'name': 'La Riua',
            'place_id': 'test_place_id'
        }
        
        # Mock Google reviews
        mock_google_reviews.return_value = [
            {'rating': 5, 'text': 'Great food!', 'source': 'google_places'},
            {'rating': 4, 'text': 'Good service', 'source': 'google_places'}
        ]
        
        # Mock TripAdvisor reviews
        mock_ta_reviews.return_value = [
            {'rating': 4, 'text': 'Nice atmosphere', 'source': 'tripadvisor'},
            {'rating': 5, 'text': 'Excellent paella', 'source': 'tripadvisor'}
        ]
        
        # Test review blending
        reviews = self.fetcher.get_reviews(self.test_business, limit=4)
        self.assertEqual(len(reviews), 4, "Should blend reviews from both sources")
        google_reviews = [r for r in reviews if r['source'] == 'google_places']
        ta_reviews = [r for r in reviews if r['source'] == 'tripadvisor']
        self.assertEqual(len(google_reviews), 2, "Should have 2 Google reviews")
        self.assertEqual(len(ta_reviews), 2, "Should have 2 TripAdvisor reviews")
    
    @patch('shared.google_places_adapter.GooglePlacesAdapter.search_business')
    @patch('shared.restaurant_data_fetcher.RestaurantDataFetcher._get_tripadvisor_competitors')
    def test_competitor_blending(self, mock_ta_competitors, mock_google_search):
        """Test competitor blending strategy."""
        # Mock Google Places business data
        mock_google_search.return_value = {
            'name': 'La Riua',
            'location': {'latitude': 39.4699, 'longitude': -0.3763}
        }
        
        # Mock TripAdvisor competitors
        mock_ta_competitors.return_value = [
            {
                'name': 'Competitor 1',
                'rating': 4.0,
                'price_level': '€€',
                'source': 'tripadvisor'
            },
            {
                'name': 'Competitor 2',
                'rating': 4.2,
                'price_level': '€€€',
                'source': 'tripadvisor'
            }
        ]
        
        # Test competitor blending
        competitors = self.fetcher.get_competitors(self.test_business)
        self.assertGreater(len(competitors), 0)
        self.assertTrue(any(c['source'] == 'tripadvisor' for c in competitors))
    
    def test_caching(self):
        """Test data caching functionality."""
        test_data = {'name': 'Test', 'rating': 4.5}
        
        # Test cache saving and retrieval
        self.fetcher._save_to_cache('test_key', test_data)
        cached = self.fetcher._get_from_cache('test_key')
        self.assertEqual(cached, test_data)
        
        # Test cache expiration
        self.fetcher.cache_duration = timedelta(seconds=0)  # Immediate expiration
        expired = self.fetcher._get_from_cache('test_key')
        self.assertIsNone(expired)

if __name__ == '__main__':
    unittest.main()
