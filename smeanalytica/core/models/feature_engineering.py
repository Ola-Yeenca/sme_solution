"""Feature engineering for SME Analytica models."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import logging

class FeatureEngineering:
    """Feature engineering for various analysis types."""
    
    def __init__(self):
        """Initialize feature engineering."""
        self.scaler = StandardScaler()
    
    def prepare_pricing_features(self, business_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare features for pricing analysis."""
        try:
            # Extract business features
            business_features = {
                'rating': float(business_data.get('rating', 0)),
                'review_count': int(business_data.get('review_count', 0)),
                'capacity': int(business_data.get('capacity', 0)),
                'years_in_business': self._calculate_years_in_business(business_data.get('established_date')),
                'premium_features': len(business_data.get('amenities', [])),
                'current_price': float(business_data.get('current_price', 0))
            }
            
            # Calculate competitor statistics
            competitor_stats = self._calculate_competitor_stats(competitors)
            
            # Calculate price distribution
            price_distribution = self._calculate_price_distribution(competitors)
            
            # Calculate real-time factors
            real_time_factors = self._calculate_real_time_factors(business_data)
            
            # Combine all features
            features = {
                'business_metrics': business_features,
                'competitor_stats': competitor_stats,
                'price_distribution': price_distribution,
                'real_time_factors': real_time_factors
            }
            
            return features
            
        except Exception as e:
            logging.error(f"Error preparing pricing features: {str(e)}")
            return {}
    
    def prepare_forecast_features(self, historical_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for sales forecasting."""
        # Convert historical data to DataFrame
        df = pd.DataFrame(historical_data['sales'])
        
        # Add time-based features
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Add lag features
        for lag in [1, 7, 30]:  # Daily, weekly, monthly lags
            df[f'sales_lag_{lag}'] = df['sales'].shift(lag)
        
        # Add rolling statistics
        for window in [7, 30]:  # Weekly and monthly windows
            df[f'sales_mean_{window}d'] = df['sales'].rolling(window=window).mean()
            df[f'sales_std_{window}d'] = df['sales'].rolling(window=window).std()
        
        # Handle missing values from lag features
        df = df.fillna(method='bfill')
        
        # Add seasonal features
        df['season'] = df['month'].map(self._get_season)
        season_dummies = pd.get_dummies(df['season'], prefix='season')
        df = pd.concat([df, season_dummies], axis=1)
        
        # Select features for model
        feature_cols = [
            'month', 'day_of_week', 'is_weekend',
            'sales_lag_1', 'sales_lag_7', 'sales_lag_30',
            'sales_mean_7d', 'sales_std_7d',
            'sales_mean_30d', 'sales_std_30d'
        ] + [col for col in df.columns if col.startswith('season_')]
        
        # Scale features
        features = df[feature_cols].values
        return self.scaler.fit_transform(features)
    
    def _prepare_forecast_features(self, historical_sales: pd.DataFrame) -> np.ndarray:
        """Prepare features for sales forecasting."""
        # Convert date to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(historical_sales['date']):
            historical_sales['date'] = pd.to_datetime(historical_sales['date'])
        
        # Extract temporal features
        features = pd.DataFrame()
        features['day_of_week'] = historical_sales['date'].dt.dayofweek
        features['month'] = historical_sales['date'].dt.month
        features['is_weekend'] = (historical_sales['day_type'] == 'weekend').astype(int)
        features['is_holiday'] = (historical_sales['day_type'] == 'holiday').astype(int)
        
        # Weather features (one-hot encoding)
        weather_dummies = pd.get_dummies(historical_sales['weather'], prefix='weather')
        features = pd.concat([features, weather_dummies], axis=1)
        
        # Event features (one-hot encoding)
        event_dummies = pd.get_dummies(historical_sales['events'], prefix='event')
        features = pd.concat([features, event_dummies], axis=1)
        
        # Add lagged sales (previous day, previous week)
        features['sales_lag1'] = historical_sales['sales'].shift(1).fillna(0)
        features['sales_lag7'] = historical_sales['sales'].shift(7).fillna(0)
        
        # Add rolling means
        features['sales_ma7'] = historical_sales['sales'].rolling(window=7, min_periods=1).mean()
        features['sales_ma30'] = historical_sales['sales'].rolling(window=30, min_periods=1).mean()
        
        # Scale numerical features
        numerical_cols = ['sales_lag1', 'sales_lag7', 'sales_ma7', 'sales_ma30']
        features[numerical_cols] = self.scaler.fit_transform(features[numerical_cols])
        
        return features.to_numpy()

    def get_config(self, features: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get feature engineering configuration.
        
        Args:
            features: Dictionary of feature names and whether they should be included
            
        Returns:
            Feature engineering configuration
        """
        config = {}
        for feature_name, include in features.items():
            if include:
                config[feature_name] = {
                    'enabled': True
                }
        return config
    
    def _calculate_years_in_business(self, established_date: str) -> float:
        """Calculate years in business from established date."""
        if not established_date:
            return 0.0
            
        try:
            established = datetime.strptime(established_date, '%Y-%m-%d')
            years = (datetime.now() - established).days / 365.25
            return round(years, 1)
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_competitor_stats(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed competitor statistics."""
        if not competitors:
            return {}
            
        try:
            prices = [float(c.get('price_level', 0)) for c in competitors if c.get('price_level')]
            ratings = [float(c.get('rating', 0)) for c in competitors if c.get('rating')]
            reviews = [int(c.get('review_count', 0)) for c in competitors if c.get('review_count')]
            
            return {
                'avg_price': np.mean(prices) if prices else 0,
                'median_price': np.median(prices) if prices else 0,
                'price_std': np.std(prices) if prices else 0,
                'avg_rating': np.mean(ratings) if ratings else 0,
                'avg_reviews': np.mean(reviews) if reviews else 0,
                'total_competitors': len(competitors),
                'price_range': {
                    'min': min(prices) if prices else 0,
                    'max': max(prices) if prices else 0
                }
            }
            
        except Exception as e:
            logging.error(f"Error calculating competitor stats: {str(e)}")
            return {}
    
    def _calculate_price_distribution(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed price distribution metrics."""
        if not competitors:
            return {}
            
        try:
            # Extract valid prices
            prices = [float(c.get('price_level', 0)) for c in competitors if c.get('price_level')]
            if not prices:
                return {}
                
            # Calculate price segments
            price_range = max(prices) - min(prices)
            segment_size = price_range / 5 if price_range > 0 else 1
            
            segments = {
                'budget': 0,
                'economy': 0,
                'mid_range': 0,
                'premium': 0,
                'luxury': 0
            }
            
            min_price = min(prices)
            for price in prices:
                relative_position = (price - min_price) / price_range if price_range > 0 else 0
                if relative_position < 0.2:
                    segments['budget'] += 1
                elif relative_position < 0.4:
                    segments['economy'] += 1
                elif relative_position < 0.6:
                    segments['mid_range'] += 1
                elif relative_position < 0.8:
                    segments['premium'] += 1
                else:
                    segments['luxury'] += 1
            
            # Calculate percentiles
            percentiles = {
                'p10': np.percentile(prices, 10),
                'p25': np.percentile(prices, 25),
                'p50': np.percentile(prices, 50),
                'p75': np.percentile(prices, 75),
                'p90': np.percentile(prices, 90)
            }
            
            return {
                'segments': segments,
                'percentiles': percentiles,
                'distribution_metrics': {
                    'mean': np.mean(prices),
                    'median': np.median(prices),
                    'std': np.std(prices),
                    'skewness': float(pd.Series(prices).skew()),
                    'kurtosis': float(pd.Series(prices).kurtosis())
                }
            }
            
        except Exception as e:
            logging.error(f"Error calculating price distribution: {str(e)}")
            return {}
    
    def _calculate_real_time_factors(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate real-time pricing factors."""
        try:
            now = datetime.now()
            
            # Time-based factors
            time_factors = {
                'hour': now.hour,
                'day_of_week': now.weekday(),
                'is_weekend': now.weekday() >= 5,
                'is_business_hours': 9 <= now.hour <= 17,
                'is_peak_hours': 11 <= now.hour <= 14 or 17 <= now.hour <= 20
            }
            
            # Demand indicators
            current_capacity = float(business_data.get('current_capacity', 0))
            max_capacity = float(business_data.get('max_capacity', 1))
            utilization = current_capacity / max_capacity if max_capacity > 0 else 0
            
            demand_factors = {
                'current_utilization': utilization,
                'demand_level': self._calculate_demand_level(utilization),
                'recent_bookings': int(business_data.get('recent_bookings', 0)),
                'waiting_list': int(business_data.get('waiting_list', 0))
            }
            
            # Special conditions
            special_conditions = {
                'has_event': bool(business_data.get('current_events')),
                'has_promotion': bool(business_data.get('active_promotions')),
                'has_holiday': self._is_holiday(now),
                'weather_impact': self._calculate_weather_impact(business_data.get('weather', {}))
            }
            
            return {
                'time_factors': time_factors,
                'demand_factors': demand_factors,
                'special_conditions': special_conditions,
                'timestamp': now.isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error calculating real-time factors: {str(e)}")
            return {}
    
    def _calculate_demand_level(self, utilization: float) -> str:
        """Calculate demand level based on utilization."""
        if utilization >= 0.9:
            return 'very_high'
        elif utilization >= 0.7:
            return 'high'
        elif utilization >= 0.4:
            return 'medium'
        elif utilization >= 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_weather_impact(self, weather: Dict[str, Any]) -> float:
        """Calculate weather impact on pricing."""
        if not weather:
            return 0.0
            
        impact_factors = {
            'sunny': 0.1,
            'cloudy': 0,
            'rainy': -0.1,
            'snowy': -0.2,
            'storm': -0.3
        }
        
        condition = weather.get('condition', '').lower()
        return impact_factors.get(condition, 0.0)
    
    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a holiday."""
        # Add holiday checking logic here
        return False
    
    def _get_season(self, month: int) -> str:
        """Get season from month number."""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
