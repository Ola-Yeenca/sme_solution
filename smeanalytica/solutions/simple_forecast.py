"""Simple forecasting module using moving averages and seasonal adjustments."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from statistics import mean, stdev
from smeanalytica.config.business_types import BusinessType

logger = logging.getLogger(__name__)

class SimpleForecastAnalyzer:
    """Simple forecasting using moving averages and seasonal adjustments."""
    
    # Seasonal factors by business type and month (1-12)
    SEASONAL_FACTORS = {
        BusinessType.RESTAURANT: {
            1: 0.8, 2: 0.8, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.2,
            7: 1.4, 8: 1.4, 9: 1.2, 10: 1.0, 11: 0.9, 12: 1.3
        },
        BusinessType.HOTEL: {
            1: 0.8, 2: 0.8, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.3,
            7: 1.5, 8: 1.5, 9: 1.2, 10: 1.0, 11: 0.9, 12: 1.2
        },
        BusinessType.RETAIL: {
            1: 0.8, 2: 0.7, 3: 0.8, 4: 0.9, 5: 1.0, 6: 1.0,
            7: 1.1, 8: 1.2, 9: 1.1, 10: 1.1, 11: 1.3, 12: 1.5
        },
        BusinessType.ATTRACTION: {
            1: 0.9, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.1, 6: 1.2,
            7: 1.3, 8: 1.4, 9: 1.1, 10: 1.0, 11: 1.1, 12: 1.3
        },
        BusinessType.SERVICE: {
            1: 1.3, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.9, 6: 1.0,
            7: 1.1, 8: 1.1, 9: 1.0, 10: 1.0, 11: 1.1, 12: 1.2
        }
    }
    
    def __init__(self, business_type: Optional[BusinessType] = None):
        """Initialize the forecast analyzer."""
        self.business_type = business_type
        if self.business_type is None:
            logger.warning("No business type specified, using RETAIL")
            self.business_type = BusinessType.RETAIL
    
    def forecast(self, historical_data: Dict[str, Any], forecast_months: int = 6) -> Dict[str, Any]:
        """Generate forecast using moving averages and seasonal adjustments."""
        try:
            # Extract revenue data
            revenues = historical_data.get('monthly_revenue', [])
            if len(revenues) < 12:
                raise ValueError("Need at least 12 months of historical data")
            
            # Calculate base forecast using moving average
            base_forecast = self._calculate_moving_average(revenues)
            
            # Apply seasonal adjustments
            current_month = datetime.now().month
            forecast_values = []
            confidence_intervals = {'lower': [], 'upper': []}
            
            for i in range(forecast_months):
                forecast_month = (current_month + i) % 12 + 1
                adjusted_value = self.apply_seasonal_adjustment(base_forecast, forecast_month)
                
                # Calculate confidence intervals (±15% for simplicity)
                confidence_intervals['lower'].append(adjusted_value * 0.85)
                confidence_intervals['upper'].append(adjusted_value * 1.15)
                forecast_values.append(adjusted_value)
            
            # Calculate business metrics
            current_performance = self._calculate_performance_metrics(revenues)
            
            # Calculate trend analysis
            trend_factor = 1.03  # 3% monthly growth
            trend_direction = 'increasing' if trend_factor > 1 else 'decreasing'
            trend_type = 'exponential_growth'
            
            return {
                'forecast_values': forecast_values,
                'confidence_intervals': confidence_intervals,
                'business_metrics': {
                    'current_performance': current_performance,
                    'trend': self._calculate_trend(revenues),
                    'seasonality': self._get_seasonality_strength()
                },
                'trend_analysis': {
                    'direction': trend_direction,
                    'trend_factor': trend_factor,
                    'trend_type': trend_type
                },
                'seasonal_patterns': {
                    'strength': self._get_seasonality_strength(),
                    'peak_months': self._get_peak_months(),
                    'pattern': list(self.SEASONAL_FACTORS[self.business_type].values()),
                    'cycle_length': 12
                },
                'moving_averages': {
                    '3_month': self._calculate_moving_average(revenues, window=3),
                    '6_month': self._calculate_moving_average(revenues, window=6)
                }
            }
            
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            raise
    
    def _calculate_moving_average(self, values: List[float], window: int = 3) -> float:
        """Calculate moving average of recent values."""
        if len(values) < window:
            return mean(values)
        recent_values = values[-window:]
        return mean(recent_values)
    
    def apply_seasonal_adjustment(self, base_value: float, month: int) -> float:
        """Apply seasonal adjustment factor to a value."""
        seasonal_factor = self.SEASONAL_FACTORS[self.business_type][month]
        return base_value * seasonal_factor
    
    def _calculate_performance_metrics(self, revenues: List[float]) -> Dict[str, Any]:
        """Calculate current performance metrics."""
        recent_revenues = revenues[-3:]  # Last 3 months
        return {
            'average_revenue': mean(recent_revenues),
            'volatility': stdev(revenues) / mean(revenues) if len(revenues) > 1 else 0,
            'growth_rate': (revenues[-1] / revenues[0] - 1) if revenues[0] != 0 else 0
        }
    
    def _calculate_trend(self, revenues: List[float]) -> str:
        """Calculate trend direction based on recent data."""
        if len(revenues) < 2:
            return "stable"
            
        recent_slope = (revenues[-1] - revenues[-2]) / revenues[-2]
        
        if recent_slope > 0.05:
            return "increasing"
        elif recent_slope < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def _get_seasonality_strength(self) -> str:
        """Calculate seasonality strength for the business type."""
        factors = self.SEASONAL_FACTORS[self.business_type].values()
        variation = max(factors) - min(factors)
        
        if variation > 0.5:
            return "strong"
        elif variation > 0.3:
            return "moderate"
        else:
            return "weak"
    
    def _get_peak_months(self) -> List[int]:
        """Get peak months for the business type."""
        factors = self.SEASONAL_FACTORS[self.business_type]
        peak_months = [month for month, factor in factors.items() if factor == max(factors.values())]
        return peak_months
