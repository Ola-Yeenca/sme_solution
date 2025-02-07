"""Analysis routes for the SME Analytica API."""

import asyncio
import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from functools import wraps
from typing import Dict, Any

from ...shared.business_analyzer_factory import BusinessAnalyzerFactory
from ...shared.decorators import require_api_key, rate_limit, cache
from ...shared.exceptions import ValidationError, AnalysisError
from ...core.exceptions import BusinessAnalysisError
from ...core.analyzers.business_analyzer import BusinessAnalyzer

logger = logging.getLogger(__name__)

bp = Blueprint('analysis', __name__, url_prefix='/analysis')

# Create analyzer factory
analyzer_factory = BusinessAnalyzerFactory()

class AnalysisRequest:
    """Analysis request model."""
    def __init__(self, business_name: str, business_type: str, location: str, analysis_type: str):
        self.business_name = business_name
        self.business_type = business_type
        self.location = location
        self.analysis_type = analysis_type

def should_force_refresh() -> bool:
    """Check if we should force a refresh based on request headers."""
    if 'Cache-Control' in request.headers:
        cache_control = request.headers['Cache-Control'].lower()
        return 'no-cache' in cache_control or 'no-store' in cache_control
    return False

@bp.route('/analyze', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000'], methods=['POST', 'OPTIONS'], allow_headers=['Content-Type', 'X-API-Key'])
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
@cache(ttl=3600)  # 1 hour cache
def analyze():
    """Analyze business data."""
    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        # Get request data
        data = request.get_json()
        business_type = data.get('business_type')
        analysis_type = data.get('analysis_type')
        force_refresh = data.get('force_refresh', False) or should_force_refresh()
        
        # Check for required fields
        if not business_type or not analysis_type:
            raise ValueError("Missing required fields: business_type and analysis_type")
        
        # Run everything in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Create analyzer with force_refresh flag
            analyzer = loop.run_until_complete(
                analyzer_factory.create_analyzer(
                    business_type=business_type,
                    analysis_type=analysis_type,
                    force_refresh=force_refresh
                )
            )
            
            # Perform analysis
            result = loop.run_until_complete(analyzer.analyze(data))
        finally:
            loop.close()
        
        if not result.success:
            logger.error(f"Analysis failed: {result.error}")
            return jsonify({
                'success': False,
                'error': str(result.error)
            }), 400
        
        response = jsonify({
            'success': True,
            'data': result.data
        })
        
        # Set cache control headers
        if force_refresh:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/market', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], methods=['POST', 'OPTIONS'], allow_headers=['Content-Type', 'X-API-Key'])
@require_api_key
def analyze_market():
    """
    Analyze market conditions and opportunities.
    
    Returns:
        Analysis results
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Validate required fields
        required_fields = ['business_type', 'location']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Get analyzer
        analyzer = analyzer_factory.create_analyzer(
            data.get('business_type', '').lower(),
            'market'
        )

        # Get market analysis result
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(analyzer.analyze(data))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Market analysis error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Failed to analyze market data'
            }), 500

        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error or 'Market analysis failed'
            }), 500

        # Convert result to response format
        response_data = result.to_dict()
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Unexpected error in market analysis: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while analyzing market data'
        }), 500

@bp.route('/business', methods=['POST'])
@cross_origin()
@require_api_key
async def analyze_business():
    """
    Analyze specific business aspects.
    
    Returns:
        Analysis results
    """
    try:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'error': 'Request must be JSON'
            }), 400

        data = request.get_json()
        force_refresh = data.get('force_refresh', False) or should_force_refresh()
        
        analysis_request = AnalysisRequest(
            business_name=data['business_name'],
            business_type=data['business_type'],
            location=data.get('location'),
            analysis_type=data.get('analysis_type', 'general')
        )

        analyzer = await analyzer_factory.create_analyzer(
            business_type=analysis_request.business_type,
            analysis_type=analysis_request.analysis_type,
            force_refresh=force_refresh
        )
        
        if analysis_request.analysis_type == "competition":
            result = await analyzer.analyze_competition(analysis_request.business_name)
        elif analysis_request.analysis_type == "pricing":
            result = await analyzer.analyze_pricing(analysis_request.business_name)
        elif analysis_request.analysis_type == "sentiment":
            result = await analyzer.analyze_sentiment(analysis_request.business_name)
        else:
            result = await analyzer.analyze_general(analysis_request.business_name)
            
        response = jsonify({
            'status': 'success',
            'data': result.__dict__
        })
        
        # Set cache control headers
        if force_refresh:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
        return response
        
    except Exception as e:
        logger.error(f"Error in business analysis: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Business Analysis Failed',
            'message': str(e)
        }), 500
