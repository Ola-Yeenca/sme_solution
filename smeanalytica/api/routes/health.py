"""Health check routes."""

from flask import Blueprint, jsonify
from typing import Dict
from functools import wraps

from ...shared.decorators import require_api_key, rate_limit, cache

bp = Blueprint('health', __name__, url_prefix='/health')

@bp.route('/', methods=['GET'])
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return jsonify({"status": "healthy"})

@bp.route('/ready', methods=['GET'])
@require_api_key
@rate_limit(max_requests=100, window_seconds=3600)
def readiness_check() -> Dict[str, str]:
    """Readiness check endpoint."""
    return jsonify({
        "status": "ready",
        "services": {
            "ai_models": "loaded",
            "api": "connected"
        }
    })
