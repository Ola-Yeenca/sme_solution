"""
SME Analytica - Business Analysis Platform
"""

import os
from pathlib import Path
from dotenv import load_dotenv

__version__ = "0.1.0"

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Validate required environment variables
required_vars = {
    'OPENROUTER_API_KEY': 'API key for OpenRouter AI models',
    'GOOGLE_PLACES_API_KEY': 'API key for Google Places API',
    'RAPIDAPI_KEY': 'API key for RapidAPI services'
}

missing_vars = []
for var, description in required_vars.items():
    if not os.getenv(var):
        missing_vars.append(f"{var} ({description})")
        
if missing_vars:
    raise ValueError(
        "Missing required environment variables:\n" +
        "\n".join(f"- {var}" for var in missing_vars)
    )
