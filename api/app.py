from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv
from shared.business_analyzer_factory import BusinessAnalyzerFactory
from shared.restaurant_data_fetcher import RestaurantDataFetcher
from shared.hotel_data_fetcher import HotelDataFetcher
from shared.tourist_data_fetcher import TouristAttractionDataFetcher
from config.business_types import BusinessType
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import datetime

load_dotenv()

# Get the absolute path to the web directory
WEB_DIR = Path(__file__).parent.parent / 'web'

# Initialize Flask app with web directory as static folder
app = Flask(__name__, 
    static_url_path='',
    static_folder=str(WEB_DIR)  # Convert Path to string
)
CORS(app)

# Data fetcher mapping
DATA_FETCHERS = {
    'restaurant': RestaurantDataFetcher,
    'hotel': HotelDataFetcher,
    'attraction': TouristAttractionDataFetcher
}

@app.route('/')
def index():
    """Serve the main application page."""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        app.logger.error(f"Error serving index.html: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'File not found',
            'message': 'Could not find index.html',
            'web_dir': str(WEB_DIR)
        }), 404

# Add route for other static files
@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files from the web directory."""
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        app.logger.error(f"Error serving {filename}: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'File not found',
            'message': f'Could not find {filename}'
        }), 404

@app.route('/api/v1/analyze/<analysis_type>', methods=['POST'])
def analyze(analysis_type):
    """Analyze a business based on the specified analysis type."""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Invalid request',
                'message': 'Request body must contain valid JSON data'
            }), 400
            
        business_name = data.get('business_name')
        business_type = data.get('business_type', 'restaurant')
        
        if not business_name:
            return jsonify({
                'status': 'error',
                'error': 'Missing business name',
                'message': 'The business_name field is required'
            }), 400
            
        # Validate business type
        if business_type not in DATA_FETCHERS:
            return jsonify({
                'status': 'error',
                'error': 'Invalid business type',
                'message': f'Business type must be one of: {", ".join(DATA_FETCHERS.keys())}'
            }), 400
            
        # Convert string to BusinessType enum
        try:
            business_type_enum = BusinessType[business_type.upper()]
        except KeyError:
            return jsonify({
                'status': 'error',
                'error': 'Invalid business type',
                'message': f'Business type {business_type} is not supported'
            }), 400
            
        # Get the appropriate data fetcher and initialize it
        data_fetcher_class = DATA_FETCHERS[business_type]
        data_fetcher = data_fetcher_class(business_type_enum)
        
        try:
            # Create analyzer
            analyzer_factory = BusinessAnalyzerFactory(data_fetcher)
            analyzer = analyzer_factory.create_analyzer(business_type, analysis_type)
            if not analyzer:
                return jsonify({
                    'status': 'error',
                    'error': 'Invalid analysis type',
                    'message': f'Analysis type must be one of: pricing, sentiment, competitors, forecast'
                }), 400
            
            # Perform analysis
            result = analyzer.analyze(business_name)
            
            # Extract the actual analysis content from Claude's response
            if isinstance(result, dict) and 'choices' in result:
                analysis_content = result['choices'][0]['message']['content']
            else:
                analysis_content = result
                
            return jsonify({
                'status': 'success',
                'data': analysis_content
            })
            
        except Exception as e:
            app.logger.exception("Unexpected error during analysis")
            return jsonify({
                'status': 'error',
                'error': 'Internal server error',
                'message': str(e)
            }), 500
                
    except Exception as e:
        app.logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with current server time."""
    return jsonify({
        'status': 'ok',
        'time': datetime.datetime.utcnow().isoformat() + 'Z'
    })

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with a custom JSON response."""
    return jsonify({
        'status': 'error',
        'error': 'Resource not found',
        'message': 'The requested URL was not found on the server.',
        'docs_url': '/status'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with a custom JSON response."""
    return jsonify({
        'status': 'error',
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.',
        'docs_url': '/status'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors with a custom JSON response."""
    return jsonify({
        'status': 'error',
        'error': 'Method not allowed',
        'message': f'The method is not allowed for the requested URL.',
        'allowed_methods': error.valid_methods,
        'docs_url': '/status'
    }), 405

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
