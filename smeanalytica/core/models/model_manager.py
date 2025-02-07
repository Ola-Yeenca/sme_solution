"""Model management for the SME Analytica application."""

import os
import logging
from typing import Dict, Any, Optional, List
import yaml
from pathlib import Path

from .xgboost_manager import XGBoostManager
from .feature_engineering import FeatureEngineering

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages AI model selection and configuration."""
    
    def __init__(self):
        """Initialize the model manager."""
        self.config = self._load_config()
        self.xgboost_managers: Dict[str, XGBoostManager] = {}
        self.feature_engineering = FeatureEngineering()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML."""
        try:
            config_path = Path(__file__).parent / 'config' / 'models.yaml'
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading model config: {str(e)}")
            return {}
            
    def get_xgboost_manager(self, analysis_type: str) -> XGBoostManager:
        """Get or create XGBoost manager for analysis type."""
        if analysis_type not in self.xgboost_managers:
            self.xgboost_managers[analysis_type] = XGBoostManager(analysis_type)
        return self.xgboost_managers[analysis_type]
    
    def get_model(self, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Get model configuration and initialize model for analysis type.
        
        Args:
            analysis_type: Type of analysis to get model for
            
        Returns:
            Model configuration if found, None otherwise
        """
        try:
            if analysis_type not in self.config:
                logger.warning(f"No model configuration found for {analysis_type}")
                return None
                
            # Get base configuration
            config = self.config[analysis_type].copy()
            
            # Add feature engineering configuration if features are specified
            if 'features' in config:
                try:
                    config['feature_engineering'] = self.feature_engineering.get_config(config['features'])
                except Exception as e:
                    logger.error(f"Error configuring feature engineering: {str(e)}")
                    # Continue with base config if feature engineering fails
                    
            return config
            
        except Exception as e:
            logger.error(f"Error getting model configuration: {str(e)}")
            return None
