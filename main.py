"""Main Flask application for SME Analytica."""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS

from smeanalytica.shared.business_analyzer_factory import BusinessAnalyzerFactory
from smeanalytica.api.routes.data import bp as data_bp
from smeanalytica.api.routes.health import bp as health_bp
from smeanalytica.api.routes.analysis import bp as analysis_bp
from smeanalytica.exceptions import AnalysisError, BusinessAnalysisError

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # Allow all origins in development
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key", "Accept"],
        }
    })

    # Create main API blueprint
    api_bp = Blueprint('api', __name__, url_prefix='/api')

    # Register sub-blueprints with the main API blueprint
    api_bp.register_blueprint(data_bp)
    api_bp.register_blueprint(health_bp)
    api_bp.register_blueprint(analysis_bp)

    # Register the main API blueprint with the app
    app.register_blueprint(api_bp)

    # Create analyzer factory
    analyzer_factory = BusinessAnalyzerFactory()

    @app.before_request
    def startup():
        """Initialize application resources."""
        try:
            # Get environment
            env = os.getenv('FLASK_ENV', 'development')
            
            # Check for required environment variables in development
            if env == 'development':
                required_vars = ['OPENROUTER_API_KEY']
                missing_vars = [var for var in required_vars if not os.getenv(var)]
                if missing_vars:
                    logger.warning(f"Missing environment variables in development mode: {', '.join(missing_vars)}")
                    if request.path.startswith('/health'):
                        return  # Allow health checks to proceed
            else:
                # In production, raise an error for missing required variables
                required_vars = ['OPENROUTER_API_KEY']
                missing_vars = [var for var in required_vars if not os.getenv(var)]
                if missing_vars:
                    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
                
            logger.info("Application startup complete")
            
        except Exception as e:
            logger.error(f"Startup failed: {str(e)}")
            if os.getenv('ENVIRONMENT') != 'development':
                raise

    @app.teardown_appcontext
    def shutdown(exception=None):
        """Clean up application resources."""
        if exception:
            logger.error(f"Error during shutdown: {str(exception)}")
        logger.info("Application shutdown complete")

    @app.errorhandler(AnalysisError)
    def handle_analysis_error(error):
        """Handle analysis-specific errors."""
        return jsonify({
            'status': 'error',
            'error': 'Analysis error',
            'message': str(error)
        }), 400

    @app.errorhandler(BusinessAnalysisError)
    def handle_business_analysis_error(error):
        """Handle business analysis specific errors."""
        return jsonify({
            'status': 'error',
            'error': 'Business analysis error',
            'message': str(error)
        }), 400

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)