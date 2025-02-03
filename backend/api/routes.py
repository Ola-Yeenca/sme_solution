from flask import Blueprint, jsonify, request
from .location_service import LocationService
import os

api = Blueprint('api', __name__)
location_service = LocationService()

@api.route('/stats/<city>')
def get_city_stats(city):
    """Get business statistics for a specific city."""
    try:
        stats = location_service.get_location_stats(city)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/demo/register', methods=['POST'])
def register_demo():
    """Register for a demo with location data."""
    try:
        data = request.get_json()
        # Here you would typically:
        # 1. Validate the data
        # 2. Store in your database
        # 3. Send confirmation email
        # 4. Trigger any necessary analytics
        
        # For now, just log and return success
        print(f"Demo registration received: {data}")
        return jsonify({
            'status': 'success',
            'message': 'Demo registration received'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/location/search')
def search_location():
    """Search for a location and get relevant business data."""
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
        
    try:
        # This would typically integrate with various data sources
        # For now, return mock data
        return jsonify({
            'locations': [
                {
                    'name': query,
                    'type': 'city',
                    'country': 'Detected from query',
                    'business_count': '1000+',
                    'market_potential': 'High'
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
