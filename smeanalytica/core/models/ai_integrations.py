"""AI model integrations for SME Analytica."""

import os
import json
import logging
import aiohttp
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ModelResponse:
    """Standardized model response structure."""
    content: Dict[str, Any]
    model: str
    usage: Dict[str, int]
    latency: float

class AIModelError(Exception):
    """Custom exception for AI model errors."""
    pass

class AIModelIntegration:
    """Handles integration with various AI models."""
    
    def __init__(self):
        """Initialize AI model integration."""
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        self.openrouter_url = "https://openrouter.ai/api/v1"
        self.referer = "https://github.com/codeium/cascade"
        
    async def get_model_analysis(self, prompt: str, model: str) -> Dict[str, Any]:
        """Get analysis from a specific model via OpenRouter API."""
        try:
            logger.info(f"Sending request to {model}")
            
            # Map model names to OpenRouter model IDs
            model_map = {
                "anthropic/claude-2": "anthropic/claude-2",
                "deepseek-ai/deepseek-coder-33b-instruct": "deepseek/deepseek-chat-v3",
                "openai/gpt-4-turbo-preview": "openai/gpt-4-turbo-preview"
            }
            
            model_id = model_map.get(model)
            if not model_id:
                raise AIModelError(f"Invalid model ID: {model}")
            
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://github.com/Ola-Yeenca/sme_solution",
                "X-Title": "SME Solution Dynamic Pricing Analysis",
                "Content-Type": "application/json"
            }
            
            # Create a template for the expected response
            template = {
                "market_data": {
                    "competitor_pricing": {"average": 0.0, "range": {"min": 0.0, "max": 0.0}},
                    "customer_segments": [],
                    "demand_patterns": [],
                    "position": ""
                },
                "recommendation": {
                    "optimal_price_range": {"min": 0.0, "max": 0.0, "recommended": 0.0},
                    "price_positioning": "",
                    "seasonal_adjustments": [],
                    "special_offers": []
                },
                "metrics": {
                    "confidence": 0.0,
                    "data_freshness": 0.0,
                    "market_coverage": 0.0
                }
            }
            
            data = {
                "model": model_id,
                "messages": [
                    {
                        "role": "system",
                        "content": f"""You are a business and pricing analyst. Analyze the given data and provide insights in valid JSON format.
                        Your response must be a JSON object with this exact structure (replace values with actual analysis):
                        {json.dumps(template, indent=2)}
                        
                        IMPORTANT: Your response must:
                        1. Start with a valid JSON object (no text before or after)
                        2. Use double quotes for all strings
                        3. Use proper JSON number format (no trailing decimal points)
                        4. Have no comments or markdown formatting
                        5. Do not escape quotes in the response"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"{model} API error: {error_text}")
                        raise AIModelError(f"{model} API returned status {response.status}: {error_text}")
                    
                    response_data = await response.json()
                    logger.debug(f"{model} raw response: {response_data}")
                    
                    if not response_data.get("choices"):
                        logger.error(f"No choices in {model} response: {response_data}")
                        raise AIModelError(f"No choices in {model} response")
                    
                    analysis_text = response_data["choices"][0]["message"]["content"]
                    logger.debug(f"{model} content: {analysis_text}")
                    
                    try:
                        # Clean up the response text
                        analysis_text = analysis_text.strip()
                        
                        # Remove any markdown code block markers
                        analysis_text = re.sub(r'```json\s*|\s*```', '', analysis_text)
                        
                        # Remove any text before the first { and after the last }
                        start_idx = analysis_text.find('{')
                        end_idx = analysis_text.rfind('}') + 1
                        if start_idx != -1 and end_idx != 0:
                            analysis_text = analysis_text[start_idx:end_idx]
                        
                        # Remove escaped quotes
                        analysis_text = analysis_text.replace('\\"', '"')
                        
                        # Fix common JSON formatting issues
                        analysis_text = re.sub(r',(\s*[}\]])', r'\1', analysis_text)  # Remove trailing commas
                        analysis_text = re.sub(r':\s*None\b', ': null', analysis_text)  # Replace Python None with null
                        analysis_text = re.sub(r':\s*True\b', ': true', analysis_text)  # Replace Python True with true
                        analysis_text = re.sub(r':\s*False\b', ': false', analysis_text)  # Replace Python False with false
                        analysis_text = re.sub(r'(-?\d+)%', r'\1', analysis_text)  # Remove % signs from numbers
                        
                        # Parse the JSON
                        analysis = json.loads(analysis_text)
                        
                        # Validate the structure matches our template
                        if not all(key in analysis for key in template.keys()):
                            logger.warning(f"{model} response missing required keys")
                            raise json.JSONDecodeError("Missing required keys", analysis_text, 0)
                        
                        # Convert any string numbers to floats
                        if 'metrics' in analysis:
                            for key in ['confidence', 'data_freshness', 'market_coverage']:
                                if key in analysis['metrics']:
                                    try:
                                        analysis['metrics'][key] = float(str(analysis['metrics'][key]).rstrip('%')) / 100
                                    except (ValueError, TypeError):
                                        analysis['metrics'][key] = 0.0
                        
                        return analysis
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse {model} JSON: {str(e)}\nContent: {analysis_text}")
                        raise AIModelError(f"Failed to parse {model} analysis: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in {model} analysis: {str(e)}", exc_info=True)
            raise AIModelError(f"{model} analysis failed: {str(e)}")

@dataclass
class MarketData:
    """Market data structure."""
    competitor_pricing: Dict[str, Any]
    customer_segments: List[Dict[str, str]]
    demand_patterns: List[Dict[str, str]]
    position: str

@dataclass
class Recommendation:
    """Recommendation data structure."""
    optimal_price_range: Dict[str, float]
    price_positioning: str
    seasonal_adjustments: List[Dict[str, Any]]
    special_offers: List[Dict[str, Any]]

@dataclass
class Metrics:
    """Metrics data structure."""
    confidence: float
    data_freshness: float
    market_coverage: float

@dataclass
class AnalysisResult:
    """Analysis result structure."""
    market_data: MarketData
    recommendation: Recommendation
    metrics: Metrics

async def analyze_pricing_strategy(self, data: Dict[str, Any]) -> AnalysisResult:
    """Analyze pricing strategies using multiple AI models and combine their insights."""
    try:
        logger.info(f"Starting pricing analysis for {data.get('business_name')} ({data.get('business_type')})")
        
        # Get business type specific context
        business_type_context = self._get_business_type_context(data.get('business_type', '').lower())
        
        # Construct the analysis prompt
        prompt = self._construct_analysis_prompt(data, business_type_context)
        
        # Models to use
        models = [
            "anthropic/claude-2",
            "deepseek-ai/deepseek-coder-33b-instruct",
            "openai/gpt-4-turbo-preview"
        ]
        
        # Get analysis from all models
        analyses = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_model_analysis(prompt, model) for model in models]
            model_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in model_results:
                if not isinstance(result, Exception) and result is not None:
                    analyses.append(result)
        
        if not analyses:
            logger.error("All model analyses failed")
            return self._get_default_analysis(data, business_type_context)
        
        # Combine the analyses
        combined = self._combine_model_analyses(analyses)
        
        # Create proper data structures
        market_data = MarketData(
            competitor_pricing=combined['market_data']['competitor_pricing'],
            customer_segments=combined['market_data']['customer_segments'],
            demand_patterns=combined['market_data']['demand_patterns'],
            position=combined['market_data']['position']
        )
        
        recommendation = Recommendation(
            optimal_price_range=combined['recommendation']['optimal_price_range'],
            price_positioning=combined['recommendation']['price_positioning'],
            seasonal_adjustments=combined['recommendation']['seasonal_adjustments'],
            special_offers=combined['recommendation']['special_offers']
        )
        
        metrics = Metrics(
            confidence=float(combined['metrics']['confidence']),
            data_freshness=float(combined['metrics']['data_freshness']),
            market_coverage=float(combined['metrics']['market_coverage'])
        )
        
        return AnalysisResult(
            market_data=market_data,
            recommendation=recommendation,
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Error in pricing analysis: {str(e)}", exc_info=True)
        return self._get_default_analysis(data, business_type_context)

    # Rest of the code remains the same...
