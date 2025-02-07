"""Data source management for the SME Analytica application."""

import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path
import time
from collections import OrderedDict
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

class DataSourceError(Exception):
    """Custom exception for data source errors."""
    pass

class DataSourceManager:
    """Manages data source selection and retrieval."""
    
    def __init__(self):
        """Initialize data source manager."""
        # Load environment variables
        env_path = Path(__file__).parents[3] / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # Initialize API keys
        self.google_places_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.google_places_key:
            logger.warning("GOOGLE_PLACES_API_KEY not found in environment variables")
            
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_key:
            logger.warning("OPENROUTER_API_KEY not found in environment variables")
            
        self.rapid_api_key = os.getenv('RAPIDAPI_KEY')
        if not self.rapid_api_key:
            logger.warning("RAPIDAPI_KEY not found in environment variables")
            
        self.cache = {}
        self.cache_ttl = timedelta(minutes=10)  # Reduced from 1 hour
        self.last_refresh = datetime.now()
        
        if not self.rapid_api_key:
            raise ValueError("RapidAPI key not configured")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load data source configuration from YAML."""
        config_path = Path(__file__).parent.parent.parent.parent / 'config' / 'models.yml'
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def _get_cache_key(self, business_name: str, data_type: str) -> str:
        """Generate cache key for a business and data type."""
        return f"{business_name}:{data_type}"
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if available and not expired."""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl.total_seconds():
                return data
            del self.cache[key]
        return None
    
    def _add_to_cache(self, key: str, data: Dict[str, Any]):
        """Add data to cache with timestamp."""
        self.cache[key] = (data, time.time())
    
    async def _validate_business_exists(self, business_name: str, location: str = None) -> bool:
        """Validate if a business exists using Google Places API."""
        if not self.google_places_key:
            logger.error("Google Places API key not found in environment variables")
            return False

        try:
            # Use Text Search API instead of Find Place for better results
            base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            
            # Include location if provided
            query = business_name
            if location:
                query = f"{business_name} in {location}"
                
            params = {
                'query': query,
                'key': self.google_places_key,
                'type': 'establishment'
            }
            
            # Log the full request URL (without API key)
            request_url = f"{base_url}?query={quote(query)}&type=establishment"
            logger.info(f"Making Places API request to: {request_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params) as response:
                    data = await response.json()
                    logger.info(f"Places API response status: {data.get('status')}")
                    logger.info(f"Places API response: {json.dumps(data, indent=2)}")
                    
                    if data.get('status') == 'REQUEST_DENIED':
                        error_msg = data.get('error_message', 'No error message')
                        logger.error(f"Google Places API request denied. Error: {error_msg}")
                        return False
                        
                    if data.get('status') == 'OK' and data.get('results'):
                        logger.info(f"Found {len(data['results'])} matching places")
                        for place in data['results']:
                            logger.info(f"Found place: {place.get('name')} at {place.get('formatted_address')}")
                        return True
                        
                    logger.warning(f"Place search failed: {data.get('status')} - {data.get('error_message', 'No error message')}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error validating business: {str(e)}", exc_info=True)
            return False

    async def get_business_data(self, business_name: str, business_type: str = None, location: str = None, force_refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive business data from available sources."""
        try:
            cache_key = self._get_cache_key(business_name, 'business_data')
            
            if not force_refresh:
                cached_data = self._get_from_cache(cache_key)
                if cached_data:
                    return cached_data

            # Initialize response data
            data = {
                "name": business_name,
                "type": business_type,
                "location": location,
                "rating": None,
                "price_level": None,
                "competitors": [],
                "market_data": {}
            }

            # First try Google Places API
            try:
                places_data = await self._get_places_data(business_name, location)
                if places_data:
                    data.update(places_data)
                    logger.info(f"Successfully retrieved Places data for {business_name}")
                else:
                    logger.warning(f"No Places data found for {business_name}")
            except Exception as e:
                logger.error(f"Failed to get Places data: {str(e)}")
                # Continue with default data

            # Then try to get competitor data
            try:
                competitor_data = await self._get_competitor_data(business_name, business_type, location)
                if competitor_data:
                    data["competitors"] = competitor_data
                    logger.info(f"Found {len(competitor_data)} competitors")
                else:
                    logger.warning("No competitor data found")
            except Exception as e:
                logger.error(f"Failed to get competitor data: {str(e)}")
                # Continue with empty competitor list

            # Get market data
            try:
                market_data = await self._get_market_data(business_type, location)
                if market_data:
                    data["market_data"] = market_data
                    logger.info("Successfully retrieved market data")
                else:
                    logger.warning("No market data found")
            except Exception as e:
                logger.error(f"Failed to get market data: {str(e)}")
                # Continue with empty market data

            # Cache the results
            self._add_to_cache(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"Error getting business data: {str(e)}", exc_info=True)
            # Return basic data structure even if everything fails
            return {
                "name": business_name,
                "type": business_type,
                "location": location,
                "rating": None,
                "price_level": None,
                "competitors": [],
                "market_data": {}
            }

    async def _get_places_data(self, business_name: str, location: str = None) -> Dict[str, Any]:
        """Get data from Google Places API."""
        if not self.google_places_key:
            raise ValueError("Google Places API key not configured")

        try:
            base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            query = f"{business_name}"
            if location:
                query = f"{business_name} in {location}"

            params = {
                'query': query,
                'key': self.google_places_key,
                'type': 'establishment'
            }

            logger.info(f"Making Places API request for: {query}")
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get('status') == 'REQUEST_DENIED':
                        error_msg = data.get('error_message', 'No error message')
                        logger.error(f"Places API request denied: {error_msg}")
                        raise ValueError(f"Places API request denied: {error_msg}")

                    if data.get('status') == 'OK' and data.get('results'):
                        place = data['results'][0]  # Get the first result
                        logger.info(f"Found place: {place.get('name')} at {place.get('formatted_address')}")
                        
                        # Get detailed place information including reviews
                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {
                            'place_id': place['place_id'],
                            'key': self.google_places_key,
                            'fields': 'name,rating,reviews,price_level,formatted_address,types,business_status,user_ratings_total'
                        }
                        
                        async with session.get(details_url, params=details_params) as details_response:
                            details_data = await details_response.json()
                            if details_data.get('status') == 'OK':
                                result = details_data['result']
                                
                                # Format reviews
                                reviews = []
                                for review in result.get('reviews', []):
                                    reviews.append({
                                        'rating': review.get('rating', 0),
                                        'text': review.get('text', ''),
                                        'time_created': review.get('time', ''),
                                        'user': review.get('author_name', 'Anonymous'),
                                        'source': 'google'
                                    })
                                
                                return {
                                    "place_id": place.get('place_id'),
                                    "formatted_address": result.get('formatted_address'),
                                    "rating": result.get('rating'),
                                    "price_level": result.get('price_level', 2),
                                    "types": result.get('types', []),
                                    "reviews": reviews,
                                    "user_ratings_total": result.get('user_ratings_total', 0)
                                }
                    
                    logger.warning(f"Place search failed: {data.get('status')} - {data.get('error_message', 'No error message')}")
                    return None

        except Exception as e:
            logger.error(f"Error in Places API request: {str(e)}", exc_info=True)
            raise

    async def _get_competitor_data(self, business_name: str, business_type: str, location: str) -> List[Dict[str, Any]]:
        """Get competitor data from Google Places and Yelp."""
        try:
            if not self.google_places_key:
                logger.warning("Google Places API key not set")
                return []
                
            # First get the target business data
            target_data = await self._get_places_data(business_name, location)
            if not target_data:
                logger.warning(f"Could not find target business: {business_name}")
                return []
                
            # Search for similar businesses in the area
            search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": f"{business_type} in {location}",
                "key": self.google_places_key,
                "type": "establishment",
                "radius": "5000"  # 5km radius
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    search_data = await response.json()
                    
                    if search_data.get('status') != 'OK':
                        logger.warning(f"Competitor search failed: {search_data.get('status')}")
                        return []
                    
                    # Get details for each place
                    competitors = []
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    
                    # Add target business first
                    target_price_level = target_data.get('price_level')
                    if isinstance(target_price_level, str):
                        target_price_level = len(target_price_level)
                    elif target_price_level is None:
                        target_price_level = 2
                    
                    competitors.append({
                        'name': business_name,
                        'rating': target_data.get('rating'),
                        'price_level': target_price_level,
                        'location': target_data.get('formatted_address', ''),
                        'place_id': target_data.get('place_id', ''),
                        'is_target': True,
                        'reviews_count': target_data.get('user_ratings_total', 0),
                        'status': 'operational',
                        'distance': 0  # Target business is reference point
                    })
                    
                    # Add other businesses
                    for place in search_data.get('results', [])[:8]:  # Get top 8 competitors
                        if place['name'].lower() != business_name.lower():
                            # Get place details
                            details_params = {
                                'place_id': place['place_id'],
                                'key': self.google_places_key,
                                'fields': 'name,rating,price_level,formatted_address,business_status,user_ratings_total,geometry'
                            }
                            
                            try:
                                async with session.get(details_url, params=details_params) as details_response:
                                    details_data = await details_response.json()
                                    if details_data.get('status') == 'OK':
                                        result = details_data['result']
                                        
                                        # Handle price level conversion
                                        price_level = result.get('price_level')
                                        if isinstance(price_level, str):
                                            price_level = len(price_level)
                                        elif price_level is None:
                                            price_level = 2
                                        
                                        # Calculate distance if geometry data is available
                                        distance = 0
                                        if 'geometry' in result and 'location' in result['geometry']:
                                            # Simple distance calculation (can be enhanced with actual distance matrix)
                                            target_loc = place['geometry']['location']
                                            distance = ((target_loc['lat'] - result['geometry']['location']['lat']) ** 2 +
                                                      (target_loc['lng'] - result['geometry']['location']['lng']) ** 2) ** 0.5 * 111  # Rough km conversion
                                        
                                        competitors.append({
                                            'name': place['name'],
                                            'rating': result.get('rating'),
                                            'price_level': price_level,
                                            'location': result.get('formatted_address', ''),
                                            'place_id': place['place_id'],
                                            'is_target': False,
                                            'reviews_count': result.get('user_ratings_total', 0),
                                            'status': result.get('business_status', 'OPERATIONAL').lower(),
                                            'distance': distance
                                        })
                            except Exception as e:
                                logger.error(f"Error getting details for competitor {place['name']}: {str(e)}")
                                continue
                    
                    # Filter out competitors with missing critical data
                    valid_competitors = [comp for comp in competitors 
                                       if comp.get('rating') is not None 
                                       and comp.get('price_level') is not None
                                       and comp.get('status') == 'operational']
                    
                    logger.info(f"Found {len(valid_competitors)} valid competitors out of {len(competitors)} total")
                    return valid_competitors
                    
        except Exception as e:
            logger.error(f"Error getting competitor data: {str(e)}")
            return []

    async def _get_market_data(self, business_type: str, location: str) -> Dict[str, Any]:
        """Get market data including trends and metrics."""
        try:
            # Get current month for seasonal analysis
            current_month = datetime.now().month
            
            # Define seasonal factors
            seasonal_factors = {
                'restaurant': {
                    'winter': [12, 1, 2],
                    'spring': [3, 4, 5],
                    'summer': [6, 7, 8],
                    'fall': [9, 10, 11],
                    'peak_months': [7, 8, 12],  # Summer and December
                },
                'cafe': {
                    'winter': [12, 1, 2],
                    'spring': [3, 4, 5],
                    'summer': [6, 7, 8],
                    'fall': [9, 10, 11],
                    'peak_months': [6, 7, 8],  # Summer months
                },
                'retail': {
                    'winter': [12, 1, 2],
                    'spring': [3, 4, 5],
                    'summer': [6, 7, 8],
                    'fall': [9, 10, 11],
                    'peak_months': [11, 12],  # Holiday season
                },
                'fitness': {
                    'winter': [12, 1, 2],
                    'spring': [3, 4, 5],
                    'summer': [6, 7, 8],
                    'fall': [9, 10, 11],
                    'peak_months': [1, 2],  # New Year resolutions
                }
            }
            
            # Get seasonal data for business type
            business_seasons = seasonal_factors.get(business_type.lower(), {
                'winter': [12, 1, 2],
                'spring': [3, 4, 5],
                'summer': [6, 7, 8],
                'fall': [9, 10, 11],
                'peak_months': [7, 8],
            })
            
            # Determine current season and if it's peak month
            current_season = next(
                (season for season, months in business_seasons.items() 
                 if current_month in months and season != 'peak_months'),
                'unknown'
            )
            is_peak_month = current_month in business_seasons.get('peak_months', [])
            
            # Calculate market metrics
            market_size = self._calculate_market_size(business_type, location)
            growth_rate = self._calculate_growth_rate(business_type, current_season, is_peak_month)
            market_share = 0.0  # This would need actual business data to calculate
            
            # Define market trends based on business type and season
            trends = self._get_market_trends(business_type, current_season, is_peak_month)
            
            # Define market opportunities
            opportunities = self._get_market_opportunities(business_type, current_season, is_peak_month)
            
            return {
                'market_size': market_size,
                'growth_rate': growth_rate,
                'market_share': market_share,
                'trends': trends,
                'opportunities': opportunities,
                'season': current_season,
                'is_peak_season': is_peak_month
            }
            
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return {}
            
    def _calculate_market_size(self, business_type: str, location: str) -> str:
        """Calculate approximate market size."""
        # This would ideally use real market data
        base_sizes = {
            'restaurant': '€5M - €8M',
            'cafe': '€2M - €4M',
            'retail': '€10M - €15M',
            'fitness': '€3M - €6M',
        }
        return base_sizes.get(business_type.lower(), '€5M - €10M')
        
    def _calculate_growth_rate(self, business_type: str, season: str, is_peak: bool) -> float:
        """Calculate growth rate based on business type and season."""
        base_rates = {
            'restaurant': 0.05,
            'cafe': 0.04,
            'retail': 0.03,
            'fitness': 0.06,
        }
        
        base_rate = base_rates.get(business_type.lower(), 0.04)
        seasonal_multiplier = 1.5 if is_peak else 1.0
        return base_rate * seasonal_multiplier
        
    def _get_market_trends(self, business_type: str, season: str, is_peak: bool) -> List[str]:
        """Get relevant market trends."""
        trends = []
        
        # Add general trends
        if is_peak:
            trends.append(f"Peak season for {business_type} businesses")
        
        # Add business-specific trends
        business_trends = {
            'restaurant': [
                "Increasing demand for outdoor dining",
                "Growing preference for local ingredients",
                "Rise in mobile ordering and delivery",
                "Focus on sustainable practices"
            ],
            'cafe': [
                "Growing specialty coffee market",
                "Increased demand for plant-based options",
                "Rising popularity of breakfast items",
                "Trend towards cozy, work-friendly spaces"
            ],
            'retail': [
                "Growth in omnichannel shopping",
                "Increasing mobile commerce",
                "Demand for personalized experiences",
                "Focus on sustainable products"
            ],
            'fitness': [
                "Rise in hybrid gym memberships",
                "Growing demand for personal training",
                "Increased focus on wellness programs",
                "Trend towards boutique fitness experiences"
            ]
        }
        
        trends.extend(business_trends.get(business_type.lower(), [
            "Growing market demand",
            "Increasing digital adoption",
            "Focus on customer experience",
            "Trend towards personalization"
        ]))
        
        return trends[:5]  # Return top 5 trends
        
    def _get_market_opportunities(self, business_type: str, season: str, is_peak: bool) -> List[str]:
        """Get relevant market opportunities."""
        opportunities = []
        
        # Add seasonal opportunities
        if is_peak:
            opportunities.append(f"Capitalize on peak season demand with special offerings")
        
        # Add business-specific opportunities
        business_opportunities = {
            'restaurant': [
                "Expand delivery and takeout services",
                "Develop seasonal menu items",
                "Create unique dining experiences",
                "Partner with local suppliers"
            ],
            'cafe': [
                "Introduce seasonal beverage specials",
                "Expand breakfast and brunch options",
                "Create loyalty program",
                "Develop catering services"
            ],
            'retail': [
                "Enhance online presence",
                "Implement omnichannel strategy",
                "Develop private label products",
                "Create personalized shopping experiences"
            ],
            'fitness': [
                "Introduce hybrid membership options",
                "Develop corporate wellness programs",
                "Create specialized fitness classes",
                "Implement digital fitness solutions"
            ]
        }
        
        opportunities.extend(business_opportunities.get(business_type.lower(), [
            "Expand service offerings",
            "Implement digital solutions",
            "Develop customer loyalty programs",
            "Create personalized experiences"
        ]))
        
        return opportunities[:5]  # Return top 5 opportunities

    async def get_reviews(self, business_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get business reviews from available sources."""
        cache_key = self._get_cache_key(business_name, 'reviews')
        
        # Check cache first
        if cached := self._get_from_cache(cache_key):
            return cached
        
        all_reviews = []
        errors = []
        
        # Try Google Places first
        try:
            places_data = await self._get_places_data(business_name)
            if places_data and places_data.get('reviews'):
                all_reviews.extend(places_data['reviews'])
                logger.info(f"Found {len(places_data['reviews'])} reviews from Google Places")
        except Exception as e:
            errors.append(f"google_places: {str(e)}")
        
        # If we don't have enough reviews, try Yelp
        if len(all_reviews) < limit:
            try:
                yelp_reviews = await self._get_reviews_from_yelp(business_name)
                all_reviews.extend(yelp_reviews)
                logger.info(f"Found {len(yelp_reviews)} reviews from Yelp")
            except Exception as e:
                errors.append(f"yelp: {str(e)}")
        
        # If still not enough, try TripAdvisor
        if len(all_reviews) < limit:
            try:
                tripadvisor_reviews = await self._get_reviews_from_tripadvisor(business_name)
                all_reviews.extend(tripadvisor_reviews)
                logger.info(f"Found {len(tripadvisor_reviews)} reviews from TripAdvisor")
            except Exception as e:
                errors.append(f"tripadvisor: {str(e)}")
        
        if not all_reviews:
            logger.warning(f"No reviews found for {business_name}. Errors: {'; '.join(errors)}")
            # Return a more informative default review
            return [{
                'rating': 3.0,
                'text': f"No reviews found. Please note that this is a default placeholder. Errors: {'; '.join(errors)}",
                'time_created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': 'System',
                'source': 'default'
            }]
            
        # Sort by most recent and limit
        all_reviews.sort(key=lambda x: x.get('time_created', ''), reverse=True)
        all_reviews = all_reviews[:limit]
        
        # Cache the results
        self._add_to_cache(cache_key, all_reviews)
        
        return all_reviews
    
    async def get_competitors(self, business_name: str, location: str = None) -> List[Dict[str, Any]]:
        """Get competitors for a business from available data sources."""
        try:
            # Check cache first
            cache_key = self._get_cache_key(business_name, 'competitors')
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Get business data to find location if not provided
            if not location:
                business_data = await self.get_business_data(business_name)
                location = business_data.get('location', {}).get('formatted_address', '')
            
            competitors = []
            
            # Get competitors from Google Places
            if self.google_places_key:
                try:
                    competitors.extend(await self._get_competitors_from_google(business_name, location))
                except Exception as e:
                    self._log_error(f"Error getting Google Places competitors: {str(e)}")
            
            # Get competitors from Yelp
            if self.rapid_api_key:
                try:
                    from smeanalytica.shared.yelp_adapter import YelpAdapter
                    yelp = YelpAdapter()
                    yelp_competitors = await yelp.get_competitors(business_name, location)
                    competitors.extend(yelp_competitors)
                except Exception as e:
                    self._log_error(f"Error getting Yelp competitors: {str(e)}")
            
            # Remove duplicates based on business name
            seen_names = set()
            unique_competitors = []
            for comp in competitors:
                name = comp.get('name', '').lower()
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_competitors.append(comp)
            
            # Sort by rating (descending) and price_level (ascending)
            unique_competitors.sort(
                key=lambda x: (
                    float(x.get('rating', 0)),
                    -float(x.get('price_level', 5))
                ),
                reverse=True
            )
            
            # Cache the results
            self._add_to_cache(cache_key, unique_competitors)
            
            return unique_competitors
            
        except Exception as e:
            self._log_error(f"Error getting competitors: {str(e)}")
            return []
    
    def _log_error(self, message: str):
        """Log error message."""
        logger.error(message)
    
    async def _get_from_google_places(self, business_name: str) -> Dict[str, Any]:
        """Get business data from Google Places API."""
        try:
            base_url = "https://maps.googleapis.com/maps/api/place"
            
            # First, search for the business with enhanced parameters
            search_url = f"{base_url}/textsearch/json"
            
            # Try different search strategies
            search_strategies = [
                {'query': business_name},  # Basic search
                {'query': f"{business_name} restaurant"},  # Add business type
                {'query': f"{business_name} business"},  # Generic business search
                {'query': f"restaurant {business_name}"},  # Different word order
                {'query': business_name.replace(" ", "+")},  # Replace spaces with plus
            ]
            
            place_result = None
            error_messages = []
            
            async with aiohttp.ClientSession() as session:
                # Try each search strategy until we find results
                for strategy in search_strategies:
                    try:
                        params = {
                            **strategy,
                            'key': self.google_places_key
                        }
                        
                        async with session.get(search_url, params=params) as response:
                            if response.status != 200:
                                error_messages.append(f"API error {response.status} for query: {strategy['query']}")
                                continue
                            
                            data = await response.json()
                            if data.get('results'):
                                place_result = data['results'][0]
                                break
                            else:
                                error_messages.append(f"No results for query: {strategy['query']}")
                    
                    except Exception as e:
                        error_messages.append(f"Error with query '{strategy['query']}': {str(e)}")
                        continue
                
                if not place_result:
                    # If no results found, return default data
                    return {
                        'name': business_name,
                        'rating': 4.0,  # Default rating
                        'reviews': [],
                        'price_level': 2,  # Default price level (mid-range)
                        'address': 'Address not found',
                        'business_type': ['business'],
                        'status': 'OPERATIONAL',
                        'error': f"Business not found. Tried: {'; '.join(error_messages)}"
                    }
                
                # Get detailed place information
                details_url = f"{base_url}/details/json"
                params = {
                    'place_id': place_result['place_id'],
                    'key': self.google_places_key,
                    'fields': 'name,rating,reviews,price_level,formatted_address,types,business_status,opening_hours'
                }
                
                async with session.get(details_url, params=params) as response:
                    if response.status != 200:
                        raise DataSourceError(f"Google Places API error: {response.status}")
                    
                    details = await response.json()
                    if 'result' not in details:
                        raise DataSourceError("No details found")
                    
                    result = details['result']
                    return {
                        'name': result.get('name', business_name),
                        'rating': result.get('rating', 4.0),
                        'reviews': result.get('reviews', []),
                        'price_level': result.get('price_level', 2),
                        'address': result.get('formatted_address', 'Address not found'),
                        'business_type': result.get('types', ['business']),
                        'status': result.get('business_status', 'OPERATIONAL'),
                        'opening_hours': result.get('opening_hours', {}),
                        'source': 'google_places'
                    }
                    
        except Exception as e:
            # Return default data with error message
            return {
                'name': business_name,
                'rating': 4.0,
                'reviews': [],
                'price_level': 2,
                'address': 'Address not found',
                'business_type': ['business'],
                'status': 'OPERATIONAL',
                'error': f"Error fetching from Google Places: {str(e)}",
                'source': 'default'
            }
    
    async def _get_reviews_from_yelp(self, business_name: str) -> List[Dict[str, Any]]:
        """Get reviews from Yelp API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.rapid_api_key}',
                'Content-Type': 'application/json'
            }
            
            # First, search for the business
            search_url = "https://api.yelp.com/v3/businesses/search"
            params = {
                'term': business_name,
                'limit': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise DataSourceError(f"Yelp API error: {response.status}")
                    
                    data = await response.json()
                    if not data.get('businesses'):
                        raise DataSourceError("No results found")
                    
                    business_id = data['businesses'][0]['id']
                    
                    # Get reviews
                    reviews_url = f"https://api.yelp.com/v3/businesses/{business_id}/reviews"
                    async with session.get(reviews_url, headers=headers) as response:
                        if response.status != 200:
                            raise DataSourceError(f"Yelp API error: {response.status}")
                        
                        reviews_data = await response.json()
                        return reviews_data.get('reviews', [])
                        
        except Exception as e:
            raise DataSourceError(f"Error fetching from Yelp: {str(e)}")
            
    async def get_competitor_data(self, business_name: str, business_type: str) -> List[Dict[str, Any]]:
        """Get data about competitors in the area."""
        try:
            base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': f"{business_type} near {business_name}",
                'key': self.google_places_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params) as response:
                    if response.status != 200:
                        raise DataSourceError(f"Google Places API error: {response.status}")
                    
                    data = await response.json()
                    competitors = []
                    
                    for place in data.get('results', [])[:10]:  # Limit to top 10 competitors
                        competitor = {
                            'name': place.get('name'),
                            'rating': place.get('rating'),
                            'price_level': place.get('price_level'),
                            'address': place.get('formatted_address'),
                            'types': place.get('types', [])
                        }
                        competitors.append(competitor)
                    
                    return competitors
                    
        except Exception as e:
            raise DataSourceError(f"Error fetching competitor data: {str(e)}")
            
    async def _get_competitors_from_google(self, business_name: str, location: str = None) -> List[Dict[str, Any]]:
        """Get competitor data from Google Places API."""
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.google_places_key,
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel'
            }
            
            # Construct search query
            query = business_name
            if location:
                query += f" in {location}"
            
            data = {
                'textQuery': query,
                'languageCode': 'en'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://places.googleapis.com/v1/places:searchText',
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        raise DataSourceError(f"API request failed: {response.status}, message='{response.reason}', url='{response.url}'")
                    
                    result = await response.json()
                    places = result.get('places', [])
                    
                    competitors = []
                    for place in places:
                        competitor = {
                            'name': place.get('displayName', {}).get('text', ''),
                            'address': place.get('formattedAddress', ''),
                            'rating': place.get('rating', 0.0),
                            'review_count': place.get('userRatingCount', 0),
                            'price_level': place.get('priceLevel', 'PRICE_LEVEL_UNSPECIFIED'),
                            'source': 'google'
                        }
                        competitors.append(competitor)
                    
                    return competitors
                    
        except aiohttp.ClientError as e:
            raise DataSourceError(f"Google Places API request failed: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"Error getting Google Places data: {str(e)}")

    async def _get_reviews_from_tripadvisor(self, business_name: str) -> List[Dict[str, Any]]:
        """Get reviews from TripAdvisor API via RapidAPI."""
        try:
            headers = {
                'X-RapidAPI-Key': self.rapid_api_key,
                'X-RapidAPI-Host': 'tripadvisor-scraper.p.rapidapi.com'
            }
            
            # Search for the business
            search_url = 'https://tripadvisor-scraper.p.rapidapi.com/restaurants/searchLocation'
            params = {
                'query': business_name,
                'limit': '1'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise DataSourceError(f"TripAdvisor API error: {await response.text()}")
                    
                    data = await response.json()
                    locations = data.get('data', [])
                    
                    if not locations:
                        raise DataSourceError(f"Business '{business_name}' not found on TripAdvisor")
                    
                    location_id = locations[0]['locationId']
                    
                    # Get reviews for the business
                    reviews_url = 'https://tripadvisor-scraper.p.rapidapi.com/restaurants/getReviews'
                    review_params = {
                        'locationId': location_id,
                        'limit': '10'  # TripAdvisor API limit
                    }
                    
                    async with session.get(reviews_url, headers=headers, params=review_params) as reviews_response:
                        if reviews_response.status != 200:
                            raise DataSourceError(f"TripAdvisor API error: {await reviews_response.text()}")
                        
                        reviews_data = await reviews_response.json()
                        reviews = reviews_data.get('data', {}).get('reviews', [])
                        
                        return [{
                            'rating': review.get('rating', 0),
                            'text': review.get('text', ''),
                            'time_created': review.get('publishedDate', ''),
                            'user': review.get('author', {}).get('username', 'Anonymous'),
                            'source': 'tripadvisor'
                        } for review in reviews]
                        
        except aiohttp.ClientError as e:
            raise DataSourceError(f"TripAdvisor API request failed: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"Error getting TripAdvisor reviews: {str(e)}")
