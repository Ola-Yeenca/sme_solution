"""AI model configurations for the application."""

from enum import Enum
from typing import Dict, Any, Optional

class AIModel(Enum):
    """Available AI models for analysis."""
    CLAUDE_3_OPUS = "anthropic/claude-3-opus-20240229"  # Most powerful, best for complex analysis
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet-20240229"  # Balanced performance and cost
    CLAUDE_2 = "anthropic/claude-2"  # Good performance, more economical
    GPT4_TURBO = "openai/gpt-4-turbo-preview"  # Very capable, good for creative tasks
    GPT4 = "openai/gpt-4"  # Strong general-purpose model
    GPT35_TURBO = "openai/gpt-3.5-turbo"  # Fast and cost-effective
    MISTRAL_MEDIUM = "mistralai/mistral-medium"  # Fast and efficient
    
class ModelConfig:
    """Configuration for AI model usage."""
    
    @staticmethod
    def get_model_config(model: AIModel) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        return {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {
                "Authorization": "Bearer $OPENROUTER_API_KEY",
                "HTTP-Referer": "https://github.com/coderabbitai/openrouter-examples",
                "X-Title": "Valencia SME Solutions"
            },
            "model": model.value
        }
    
    @staticmethod
    def get_recommended_model(task_type: str) -> AIModel:
        """Get recommended model for a specific task type."""
        recommendations = {
            "sentiment_analysis": AIModel.CLAUDE_3_OPUS,  # Best for nuanced sentiment
            "competitor_analysis": AIModel.CLAUDE_3_SONNET,  # Good for market analysis
            "market_research": AIModel.GPT4_TURBO,  # Good for creative insights
            "customer_feedback": AIModel.CLAUDE_2,  # Cost-effective
            "general": AIModel.GPT35_TURBO  # Default option
        }
        return recommendations.get(task_type, AIModel.GPT35_TURBO)
