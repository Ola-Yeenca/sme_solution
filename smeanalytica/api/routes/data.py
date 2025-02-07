"""Data retrieval routes for the SME Analytica API."""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List
from functools import wraps
from flask_cors import cross_origin
import logging

from ...core.data import DataSourceManager
from ...shared.decorators import require_api_key, rate_limit, cache
from ...types.business_type import BusinessType

bp = Blueprint('data', __name__, url_prefix='/data')
data_manager = DataSourceManager()
logger = logging.getLogger(__name__)

class DataRequest:
    """Data request model."""
    def __init__(self, business_name: str, data_type: str):
        self.business_name = business_name
        self.data_type = data_type

@bp.route('/business', methods=['GET'])
@cross_origin()
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
@cache(ttl=86400)  # 24 hour cache
def get_business_data() -> Dict[str, Any]:
    """Get business data from available sources."""
    try:
        business_name = request.args.get('name')
        if not business_name:
            return jsonify({
                'status': 'error',
                'error': 'Missing parameter',
                'message': 'Business name is required'
            }), 400

        data = data_manager.get_business_data(business_name)
        return jsonify({
            'status': 'success',
            'data': data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Data retrieval error',
            'message': str(e)
        }), 500

@bp.route('/reviews', methods=['GET'])
@cross_origin()
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
@cache(ttl=3600)  # 1 hour cache
def get_reviews() -> Dict[str, Any]:
    """Get business reviews from available sources."""
    try:
        business_name = request.args.get('name')
        if not business_name:
            return jsonify({
                'status': 'error',
                'error': 'Missing parameter',
                'message': 'Business name is required'
            }), 400

        reviews = data_manager.get_reviews(business_name)
        return jsonify({
            'status': 'success',
            'data': reviews
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Review retrieval error',
            'message': str(e)
        }), 500

@bp.route('/types', methods=['GET'])
@cross_origin()
@require_api_key
def get_data_types() -> Dict[str, List[str]]:
    """Get available data types."""
    try:
        data_types = data_manager.get_data_types()
        return jsonify({
            'status': 'success',
            'data': data_types
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Data type retrieval error',
            'message': str(e)
        }), 500

@bp.route('/business-types', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_business_types():
    """Get list of available business types."""
    try:
        business_types = [
            'Restaurant',
            'Retail Store',
            'E-commerce',
            'Service Business',
            'Manufacturing',
            'Technology',
            'Healthcare',
            'Education',
            'Real Estate',
            'Construction'
        ]
        
        return jsonify({
            'status': 'success',
            'business_types': business_types
        })
        
    except Exception as e:
        logger.error(f"Error fetching business types: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch business types',
            'message': str(e)
        }), 500

@bp.route('/fetch', methods=['POST'])
@cross_origin()
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
@cache(ttl=3600)  # 1 hour cache
def fetch_data() -> Dict[str, Any]:
    """
    Fetch business data based on type.
    
    Args:
        request: Data request parameters
        
    Returns:
        Requested data
    """
    try:
        data = request.get_json()
        if not data or 'business_name' not in data or 'data_type' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing parameters',
                'message': 'Business name and data type are required'
            }), 400

        data_request = DataRequest(
            business_name=data['business_name'],
            data_type=data['data_type']
        )

        result = data_manager.fetch_data(data_request)
        return jsonify({
            'status': 'success',
            'data': result
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Data fetch error',
            'message': str(e)
        }), 500
