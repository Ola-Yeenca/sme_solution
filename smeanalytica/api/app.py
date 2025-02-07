"""Flask application for SME Analytica."""

import os
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

from smeanalytica.api.routes import analysis, diagnostics, pricing

# Load environment variables
env_path = Path(__file__).parents[0] / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

log_handler = RotatingFileHandler(
    log_dir / 'app.log',
    maxBytes=1024 * 1024 * 10,  # 10MB
    backupCount=5
)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
log_handler.setLevel(logging.INFO)

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        "/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True,
            "send_wildcard": False
        }
    })

    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'smeanalytica.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configure logging
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SME Analytica startup')

    # Register blueprints
    app.register_blueprint(analysis.bp, url_prefix='/api')
    app.register_blueprint(diagnostics.bp, url_prefix='/api')
    app.register_blueprint(pricing.bp, url_prefix='/api')

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

    @app.route('/api/health')
    def health_check():
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })

    return app

def init_app():
    """Initialize the Flask application."""
    app = create_app()
    return app
