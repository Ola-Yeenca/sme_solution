"""Performance monitoring utilities."""

import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Track performance metrics across system components."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._current_measure = None
        self._start_time: Optional[float] = None
        self.custom_metrics: Dict[str, Any] = {}
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager to time operations."""
        measure_data = {
            'operation': operation_name,
            'custom_metrics': {},
            'start_time': time.time(),
            'duration': 0.0
        }
        try:
            yield measure_data
        finally:
            measure_data['duration'] = time.time() - measure_data['start_time']
            self.metrics[operation_name] = measure_data
    
    @property
    def duration(self) -> float:
        """Get duration of current measurement."""
        if self._current_measure:
            return self._current_measure.get('duration', 0.0)
        return 0.0
    
    def start_operation(self, operation_name: str):
        """Start timing an operation."""
        self._start_time = time.time()
        self._current_measure = {
            'operation': operation_name,
            'start_time': self._start_time,
            'custom_metrics': {}
        }
        self.custom_metrics = {}
        
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'errors': 0,
                'last_error': None,
                'custom_metrics': {}
            }
    
    def end_operation(self):
        """End timing current operation and record metrics."""
        if not self._current_measure or not self._start_time:
            return
        
        duration = time.time() - self._start_time
        metrics = self.metrics[self._current_measure['operation']]
        
        metrics['count'] += 1
        metrics['total_time'] += duration
        metrics['min_time'] = min(metrics['min_time'], duration)
        metrics['max_time'] = max(metrics['max_time'], duration)
        
        if self.custom_metrics:
            metrics['custom_metrics'] = {
                **metrics.get('custom_metrics', {}),
                **self.custom_metrics
            }
        
        # Log performance data
        logger.info(
            f"Operation '{self._current_measure['operation']}' completed in {duration:.3f}s "
            f"(avg: {metrics['total_time']/metrics['count']:.3f}s)"
        )
        
        self._current_measure = None
        self._start_time = None
        self.custom_metrics = {}
    
    def record_error(self, error: Exception):
        """Record an error for the current operation."""
        if self._current_measure:
            self.metrics[self._current_measure['operation']]['errors'] += 1
            self.metrics[self._current_measure['operation']]['last_error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_metrics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for specific operation or all operations."""
        if operation_name:
            metrics = self.metrics.get(operation_name, {})
            if metrics:
                metrics = metrics.copy()
                if metrics.get('count', 0) > 0:
                    metrics['avg_time'] = metrics['total_time'] / metrics['count']
                return metrics
            return {}
        
        return {
            name: {
                **metrics,
                'avg_time': metrics['total_time'] / metrics['count'] if metrics.get('count', 0) > 0 else 0
            }
            for name, metrics in self.metrics.items()
        }
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self._current_measure = None
        self._start_time = None
        self.custom_metrics = {}
