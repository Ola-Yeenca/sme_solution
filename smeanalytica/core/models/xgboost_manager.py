"""XGBoost model management for SME Analytica."""

import os
import logging
from typing import Dict, Any, Optional, List
import xgboost as xgb
import numpy as np
import pandas as pd
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class XGBoostManager:
    """Manages XGBoost models for different analysis types."""
    
    def __init__(self, analysis_type: str):
        """Initialize XGBoost manager."""
        self.analysis_type = analysis_type
        self.model = None
        self.feature_columns = []
        self.target_column = None
        self.model_path = Path(__file__).parent.parent.parent / 'models' / f'{analysis_type}_xgboost.model'
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self) -> 'XGBoostManager':
        """Initialize the manager asynchronously."""
        if self.model_path.exists():
            await self.load_model()
        return self
        
    async def load_model(self) -> None:
        """Load XGBoost model from file."""
        try:
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                self.thread_pool,
                xgb.Booster,
                {'model_file': str(self.model_path)}
            )
            logger.info(f"Loaded XGBoost model for {self.analysis_type}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.model = None
            
    async def save_model(self) -> None:
        """Save XGBoost model to file."""
        if self.model:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.thread_pool,
                    self.model.save_model,
                    str(self.model_path)
                )
                logger.info(f"Saved XGBoost model for {self.analysis_type}")
            except Exception as e:
                logger.error(f"Failed to save model: {str(e)}")
                
    async def train(self, training_data: Dict[str, Any]) -> None:
        """Train XGBoost model with provided data."""
        try:
            # Extract features and target
            X = pd.DataFrame(training_data['features'])
            y = pd.Series(training_data['target'])
            
            # Store feature columns for prediction
            self.feature_columns = X.columns.tolist()
            self.target_column = training_data.get('target_column', 'target')
            
            # Create DMatrix
            loop = asyncio.get_event_loop()
            dtrain = await loop.run_in_executor(
                self.thread_pool,
                xgb.DMatrix,
                X, label=y
            )
            
            # Set parameters
            params = {
                'max_depth': 6,
                'eta': 0.3,
                'objective': 'reg:squarederror',
                'eval_metric': 'rmse'
            }
            
            # Train model
            self.model = await loop.run_in_executor(
                self.thread_pool,
                xgb.train,
                params,
                dtrain,
                num_boost_round=100
            )
            
            # Save model
            await self.save_model()
            logger.info(f"Successfully trained XGBoost model for {self.analysis_type}")
            
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            raise
            
    async def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using the XGBoost model."""
        try:
            if not self.model:
                await self.load_model()
                if not self.model:
                    raise ValueError("No model available for prediction")
                    
            # Prepare input data
            X = pd.DataFrame([input_data])
            if self.feature_columns:
                X = X[self.feature_columns]
                
            # Create DMatrix
            loop = asyncio.get_event_loop()
            dtest = await loop.run_in_executor(
                self.thread_pool,
                xgb.DMatrix,
                X
            )
            
            # Make prediction
            predictions = await loop.run_in_executor(
                self.thread_pool,
                self.model.predict,
                dtest
            )
            
            return {
                'predictions': predictions.tolist(),
                'feature_importance': await self.get_feature_importance()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
            
    async def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.model or not self.feature_columns:
            return {}
            
        try:
            loop = asyncio.get_event_loop()
            importance_scores = await loop.run_in_executor(
                self.thread_pool,
                self.model.get_score,
                importance_type='weight'
            )
            
            return {
                feature: float(score)
                for feature, score in importance_scores.items()
            }
            
        except Exception as e:
            logger.error(f"Failed to get feature importance: {str(e)}")
            return {}
