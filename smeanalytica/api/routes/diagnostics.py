from flask import Blueprint, jsonify
import os
from smeanalytica.core.data.data_source_manager import DataSourceManager

# Initialize blueprint
diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/api/v1/diagnostics')

@diagnostics_bp.route('/health', methods=['GET'])
def health_check():
    """Comprehensive system health check endpoint"""
    checks = {
        'google_places': test_google_places_connection(),
        'env_vars': check_required_environment_variables(),
        'api_endpoints': check_api_endpoints()
    }
    return jsonify(checks)

def test_google_places_connection():
    try:
        ds = DataSourceManager()
        data = ds._get_from_google_places("Test Cafe")
        return {"status": "healthy", "response": data is not None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_required_environment_variables():
    return {
        'GOOGLE_PLACES_API_KEY': bool(os.getenv('GOOGLE_PLACES_API_KEY')),
        'OPENROUTER_API_KEY': bool(os.getenv('OPENROUTER_API_KEY')),
        'RAPIDAPI_KEY': bool(os.getenv('RAPIDAPI_KEY'))
    }

def check_api_endpoints():
    return {
        'google_places': 'https://places.googleapis.com/v1/places',
        'openrouter': 'https://openrouter.ai/api/v1'
    }
