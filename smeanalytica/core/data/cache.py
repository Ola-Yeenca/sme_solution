"""Cache implementation for business data."""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class DataCache:
    """Cache for business data from various sources."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize the cache with a directory."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, source: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired."""
        try:
            cache_file = self.cache_dir / f"{source}_{key}.json"
            if not cache_file.exists():
                return None
                
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            cache_duration = timedelta(hours=24)  # 24 hour cache by default
            
            if datetime.now() - cached_time > cache_duration:
                logger.info(f"Cache expired for {key} from {source}")
                return None
                
            logger.info(f"Cache hit for {key} from {source}")
            return cached_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache: {str(e)}")
            return None
    
    def set(self, key: str, source: str, data: Dict[str, Any]):
        """Save data to cache with timestamp."""
        try:
            cache_file = self.cache_dir / f"{source}_{key}.json"
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            logger.info(f"Cached data for {key} from {source}")
            
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
    
    def clear(self, key: str = None, source: str = None):
        """Clear cache entries."""
        try:
            if key and source:
                cache_file = self.cache_dir / f"{source}_{key}.json"
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info(f"Cleared cache for {key} from {source}")
            else:
                # Clear all cache files
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                logger.info("Cleared all cache entries")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
