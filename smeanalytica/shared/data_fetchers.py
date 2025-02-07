import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Constants
VALENCIA_LOCATION_ID = "187529"  
CURRENCY_CODE = "EUR"
LANGUAGE = "en_US"


def safe_request(url, headers, params=None, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get("Retry-After", delay))
                time.sleep(retry_after)
            else:
                print(f"API request failed with status code: {response.status_code}")
                print(f"Response content: {response.text}")
                time.sleep(delay)
        except Exception as e:
            print(f"Request failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

def get_restaurant_details(business_name):
    """Get restaurant details from TripAdvisor"""
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants"
    
    
    search_attempts = [
        business_name, 
        business_name.lower(),  
        business_name.replace(" ", ""),  
        " ".join(business_name.split()[:2])  
    ]
    
    for search_query in search_attempts:
        querystring = {
            "locationId": VALENCIA_LOCATION_ID,
            "page": "1",
            "currencyCode": CURRENCY_CODE,
            "language": LANGUAGE,
            "searchQuery": search_query
        }
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
        }
        
        try:
            response = safe_request(url, headers, querystring)
            if not response:
                continue
                
            data = response.json()
            if not data.get('status', False):
                print(f"API Error: {data.get('message', 'Unknown error')}")
                continue
                
            restaurants = data.get('data', {}).get('data', [])
            if not restaurants:
                print(f"No restaurants found matching: {search_query}")
                continue
                
            
            target_restaurant = None
            for restaurant in restaurants:
                restaurant_name = restaurant['name'].lower()
                search_name = business_name.lower()
                
                
                if (restaurant_name == search_name or  
                    search_name in restaurant_name or  
                    restaurant_name in search_name):   
                    target_restaurant = restaurant
                    break
            
            if not target_restaurant and restaurants:
                
                target_restaurant = restaurants[0]
                print(f"No exact match found. Using closest match: {target_restaurant['name']}")
            
            if target_restaurant:
                
                price_tag = target_restaurant.get('priceTag', '€€')
                if price_tag:
                    price_level = len([c for c in price_tag if c == '$'])  
                    avg_price = price_level * 10  
                else:
                    avg_price = 20  
                    
                return {
                    'name': target_restaurant['name'],
                    'location_id': target_restaurant['locationId'],
                    'rating': target_restaurant.get('averageRating', 0.0),
                    'reviews_count': target_restaurant.get('userReviewCount', 0),
                    'price_level': price_tag,
                    'price_range': f"{avg_price-5}-{avg_price+5}",  
                    'cuisine': target_restaurant.get('establishmentTypeAndCuisineTags', []),
                    'address': target_restaurant.get('address', ''),
                    'phone': target_restaurant.get('phone', ''),
                    'website': target_restaurant.get('menuUrl', ''),
                    'review_snippets': [
                        review.get('reviewText', '')
                        for review in target_restaurant.get('reviewSnippets', {}).get('reviewSnippetsList', [])
                    ]
                }
                
        except Exception as e:
            print(f"Error fetching restaurant details: {str(e)}")
            continue
    
    return None

def get_tripadvisor_restaurant_data(business_name):
    """Fetch restaurant data from TripAdvisor"""
    restaurant = get_restaurant_details(business_name)
    
    if not restaurant:
        return {
            'name': business_name,
            'reviews_count': 0,
            'average_rating': 0.0,
            'price_range': '15-25',
            'error': 'Restaurant not found'
        }
    
    return {
        'name': restaurant['name'],
        'reviews_count': restaurant['reviews_count'],
        'average_rating': restaurant['rating'],
        'price_range': restaurant['price_range'],
        'price_level': restaurant['price_level'],
        'reviews': restaurant.get('review_snippets', []),
        'error': None
    }

def fetch_tripadvisor_reviews(business_name):
    """Fetch reviews for a restaurant from TripAdvisor"""
    restaurant = get_restaurant_details(business_name)
    if not restaurant:
        return []
    
    reviews = []
    for review_text in restaurant.get('review_snippets', []):
        reviews.append({
            'text': review_text,
            'rating': restaurant['rating'],  
            'date': '',  
            'title': '',  
            'is_recent': True
        })
    
    return reviews

def get_competitor_pricing(business_name):
    """Get competitor pricing from TripAdvisor"""
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants"
    querystring = {
        "locationId": VALENCIA_LOCATION_ID,
        "page": "1",
        "currencyCode": CURRENCY_CODE,
        "language": LANGUAGE
    }
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
    }
    
    try:
        response = safe_request(url, headers, querystring)
        if not response:
            return []
            
        data = response.json()
        if not data.get('status', False):
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return []
            
        competitors = []
        target_restaurant = None
        
        
        restaurants = data.get('data', {}).get('data', [])
        for restaurant in restaurants:
            if restaurant['name'].lower() == business_name.lower():
                target_restaurant = restaurant
                break
        
        
        target_price = '€€' if not target_restaurant else target_restaurant.get('priceTag', '€€')
        
        for restaurant in restaurants[:15]:  
            if restaurant['name'].lower() != business_name.lower():
                
                price_tag = restaurant.get('priceTag', '€€')
                if price_tag:
                    price_level = len([c for c in price_tag if c == '$'])  
                    avg_price = price_level * 10  
                else:
                    avg_price = 20  
                    
                competitors.append({
                    'name': restaurant['name'],
                    'price': avg_price,
                    'rating': restaurant.get('averageRating', 0.0),
                    'reviews_count': restaurant.get('userReviewCount', 0),
                    'price_level': price_tag,
                    'cuisine': restaurant.get('establishmentTypeAndCuisineTags', [])
                })
        
        
        competitors.sort(key=lambda x: (x['rating'], x['reviews_count']), reverse=True)
        return competitors[:10]  
        
    except Exception as e:
        print(f"Error fetching competitor data: {str(e)}")
        return []

def get_weather_data(city="Valencia", country="ES"):
    """Fetch weather data for Valencia"""
    try:
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {
            "main": {
                "temp": 20,
                "feels_like": 20,
                "humidity": 60
            },
            "weather": [{"description": "no data available"}]
        }

def get_event_data():
    """Fetch events from VisitValencia (placeholder)"""
    try:
        return [
            "Las Fallas Festival",
            "Valencia Food Week",
            "Local Wine Tasting Event",
            "Beach Volleyball Tournament"
        ]
    except Exception as e:
        print(f"Error fetching events data: {e}")
        return []
