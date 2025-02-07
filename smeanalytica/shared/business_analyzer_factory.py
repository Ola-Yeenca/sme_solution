"""Factory for creating business analyzers."""

import logging
import asyncio
import time
from typing import Dict, Any, Optional

from ..core.models.model_manager import ModelManager
from ..core.analyzers.business_analyzer import BusinessAnalyzer
from .exceptions import AnalysisError

logger = logging.getLogger(__name__)

class BusinessAnalyzerFactory:
    """Factory for creating business analyzers."""
    
    def __init__(self):
        """Initialize the factory."""
        self.model_manager = ModelManager()
        self._analyzers = {}
        self._last_refresh = {}
        self._lock = asyncio.Lock()
        
    async def create_analyzer(
        self,
        business_type: str,
        analysis_type: str = None,
        force_refresh: bool = False
    ) -> BusinessAnalyzer:
        """Create or retrieve a business analyzer instance."""
        async with self._lock:
            key = f"{business_type}_{analysis_type}"
            current_time = time.time()
            
            # Check if we need to refresh the analyzer
            should_refresh = (
                force_refresh or
                key not in self._analyzers or
                key not in self._last_refresh or
                current_time - self._last_refresh[key] > 300  # 5 minutes TTL
            )
            
            if should_refresh:
                logger.info(f"Creating new analyzer for {business_type} with {analysis_type}")
                self._analyzers[key] = BusinessAnalyzer(business_type)
                self._last_refresh[key] = current_time
            
            return self._analyzers[key]
    
    def clear_cache(self) -> None:
        """Clear all cached analyzers."""
        self._analyzers.clear()
        self._last_refresh.clear()
        logger.info("Analyzer cache cleared")

    def invalidate_analyzer(self, business_type: str, analysis_type: str) -> None:
        """Invalidate a specific analyzer in the cache."""
        key = f"{business_type}_{analysis_type}"
        if key in self._analyzers:
            del self._analyzers[key]
        if key in self._last_refresh:
            del self._last_refresh[key]
        logger.info(f"Invalidated analyzer cache for {key}")
