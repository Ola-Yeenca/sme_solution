"""Base analyzer class for the SME Analytica application."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MarketData:
    """Market data structure."""
    competitors: List[Dict[str, Any]] = field(default_factory=list)
    average_competitor_rating: float = 0.0
    average_competitor_price_level: str = ''
    market_position: str = ''

@dataclass
class Recommendation:
    """Recommendation data structure."""
    pricing_strategy: str = 'maintain'
    confidence: float = 0.0
    explanation: str = ''
    suggested_actions: List[str] = field(default_factory=list)

@dataclass
class AnalysisData:
    """Analysis data structure."""
    market_data: MarketData = field(default_factory=MarketData)
    recommendation: Recommendation = field(default_factory=Recommendation)

@dataclass
class AnalysisResult:
    """Standardized structure for analysis results."""
    success: bool = False
    data: Any = None  # Changed from AnalysisData to Any to support different data structures
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert the analysis result to a dictionary."""
        if not self.success:
            return {
                'success': False,
                'error': self.error or 'Unknown error occurred'
            }
        
        # If data is already a dict, return it directly
        if isinstance(self.data, dict):
            return {
                'success': True,
                'data': self.data,
                'timestamp': self.timestamp
            }
        
        # For AnalysisData type (market data and recommendations)
        if isinstance(self.data, AnalysisData):
            return {
                'success': True,
                'data': {
                    'market_data': {
                        'competitors': self.data.market_data.competitors,
                        'average_competitor_rating': self.data.market_data.average_competitor_rating,
                        'average_competitor_price_level': self.data.market_data.average_competitor_price_level,
                        'market_position': self.data.market_data.market_position
                    },
                    'recommendation': {
                        'pricing_strategy': self.data.recommendation.pricing_strategy,
                        'confidence': self.data.recommendation.confidence,
                        'explanation': self.data.recommendation.explanation,
                        'suggested_actions': self.data.recommendation.suggested_actions
                    }
                },
                'timestamp': self.timestamp
            }
        
        # For any other data type, return as is
        return {
            'success': True,
            'data': self.data,
            'timestamp': self.timestamp
        }

class BaseAnalyzer(ABC):
    """Base class for all analyzers."""
    
    def __init__(self, model: Dict[str, Any], business_type: Optional[str] = None):
        """Initialize with model configuration and optional business type."""
        self.model = model
        self.business_type = business_type

    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Perform analysis based on input data."""
        pass

    def _create_success_result(self, market_data: MarketData, recommendation: Recommendation) -> AnalysisResult:
        """Create a successful analysis result."""
        return AnalysisResult(
            success=True,
            data=AnalysisData(
                market_data=market_data,
                recommendation=recommendation
            )
        )

    def _create_error_result(self, error: str) -> AnalysisResult:
        """Create an error analysis result."""
        return AnalysisResult(
            success=False,
            error=error
        )
