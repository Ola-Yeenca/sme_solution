"""Test configuration and validation for the business analysis system."""

from dataclasses import dataclass
from typing import Dict, Any, List

from smeanalytica.types.business_type import BusinessType

@dataclass
class BusinessProfile:
    """Test profile for a business."""
    name: str
    business_type: BusinessType
    expected_metrics: Dict[str, Any]

class TestConfig:
    """Configuration for system-wide tests."""
    
    # Test business profiles
    TEST_BUSINESSES = {
        'restaurant': BusinessProfile(
            name='La Riua',
            business_type=BusinessType.RESTAURANT,
            expected_metrics={
                'min_rating': 4.0,
                'min_reviews': 100,
                'price_range': ['€€', '€€€']
            }
        ),
        'hotel': BusinessProfile(
            name='Grand Hotel',
            business_type=BusinessType.HOTEL,
            expected_metrics={
                'min_rating': 4.2,
                'min_reviews': 200,
                'price_range': ['€€€', '€€€€']
            }
        ),
        'retail': BusinessProfile(
            name='Fashion Boutique',
            business_type=BusinessType.RETAIL,
            expected_metrics={
                'min_rating': 3.8,
                'min_reviews': 50,
                'price_range': ['€€', '€€€']
            }
        )
    }
    
    # Performance benchmarks
    PERFORMANCE_BENCHMARKS = {
        'api_response_time': 2.0,  # seconds
        'cache_hit_time': 0.1,     # seconds
        'max_api_errors': 0.1,     # 10% error rate
        'min_cache_hit_rate': 0.8  # 80% cache hit rate
    }
    
    # Required fields for business data
    REQUIRED_FIELDS = [
        'name',
        'rating',
        'reviews_count',
        'price_level',
        'address'
    ]
    
    @staticmethod
    def validate_business_data(data: Dict[str, Any]) -> List[str]:
        """Validate business data against required fields and constraints."""
        errors = []
        
        # Check required fields
        for field in TestConfig.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if not errors:
            # Validate data types and ranges
            try:
                if not isinstance(data['name'], str) or not data['name'].strip():
                    errors.append("Invalid business name")
                
                rating = float(data['rating'])
                if not (0 <= rating <= 5):
                    errors.append(f"Invalid rating: {rating}")
                
                reviews = int(data['reviews_count'])
                if reviews < 0:
                    errors.append(f"Invalid reviews count: {reviews}")
                
                if not isinstance(data['price_level'], str):
                    errors.append("Invalid price level format")
                
                if not isinstance(data['address'], str) or not data['address'].strip():
                    errors.append("Invalid address")
                
            except (ValueError, TypeError) as e:
                errors.append(f"Data type validation error: {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_forecast_results(results: Dict[str, Any]) -> List[str]:
        """Validate forecast results structure and values."""
        errors = []
        
        required_fields = [
            'forecast_values',
            'confidence_intervals',
            'business_metrics'
        ]
        
        for field in required_fields:
            if field not in results:
                errors.append(f"Missing required field in forecast results: {field}")
        
        if not errors:
            try:
                # Validate forecast values
                if not isinstance(results['forecast_values'], list):
                    errors.append("Forecast values must be a list")
                elif not all(isinstance(x, (int, float)) for x in results['forecast_values']):
                    errors.append("Invalid forecast value type")
                
                # Validate confidence intervals
                intervals = results['confidence_intervals']
                if not isinstance(intervals, dict):
                    errors.append("Confidence intervals must be a dictionary")
                elif not all(k in intervals for k in ['lower', 'upper']):
                    errors.append("Missing confidence interval bounds")
                
                # Validate business metrics
                metrics = results['business_metrics']
                if not isinstance(metrics, dict):
                    errors.append("Business metrics must be a dictionary")
                elif 'current_performance' not in metrics:
                    errors.append("Missing current performance metrics")
                
            except Exception as e:
                errors.append(f"Forecast validation error: {str(e)}")
        
        # Validate trend analysis
        trend_errors = TestConfig.validate_trend_analysis(results)
        errors.extend(trend_errors)
        
        return errors
    
    @staticmethod
    def validate_trend_analysis(results: Dict[str, Any]) -> List[str]:
        """Validate trend analysis structure."""
        errors = []
        if 'trend_analysis' not in results:
            errors.append("Missing trend_analysis in forecast results")
        if 'seasonal_patterns' not in results:
            errors.append("Missing seasonal_patterns in forecast results")
        return errors
