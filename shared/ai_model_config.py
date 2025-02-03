"""Configuration for AI models used in the application."""

from enum import Enum
from typing import Dict, Any

class AIModel(Enum):
    """Available AI models for analysis."""
    CLAUDE_3_OPUS = "anthropic/claude-3-opus-20240229"  # Most powerful, best for complex analysis
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet-20240229"  # Balanced performance and cost
    CLAUDE_2 = "anthropic/claude-2"  # Good performance, more economical
    GPT4_TURBO = "openai/gpt-4-turbo-preview"  # Very capable, good for creative tasks
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
        task_models = {
            "dynamic_pricing": AIModel.CLAUDE_3_OPUS,  # Complex market analysis
            "sentiment_analysis": AIModel.CLAUDE_3_SONNET,  # Nuanced review understanding
            "competitor_analysis": AIModel.CLAUDE_3_OPUS,  # Strategic insights
            "sales_forecasting": AIModel.CLAUDE_3_OPUS,  # Complex pattern recognition
        }
        return task_models.get(task_type, AIModel.CLAUDE_3_SONNET)  # Default to balanced model
