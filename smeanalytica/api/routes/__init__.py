"""API routes initialization."""

from flask import Blueprint
from . import analysis, health, data

# Create main API blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Register sub-blueprints
api.register_blueprint(analysis.bp)
api.register_blueprint(health.bp)
api.register_blueprint(data.bp)

# Export the main blueprint
__all__ = ["api"]
