"""
Logging system for the Physics Sailing Simulator

Provides structured logging with multiple levels, file output, and performance tracking.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import functools
import time


class SimulatorLogger:
    """
    Centralized logging system for the simulator.
    
    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File and console output
    - Performance tracking
    - Structured logging with context
    """
    
    _instance: Optional['SimulatorLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once)"""
        if self._initialized:
            return
            
        self._initialized = True
        self.logger = logging.getLogger('PhysicsSimulator')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'simulator_{timestamp}.log'
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 80)
        self.logger.info("Physics Sailing Simulator - Logging System Initialized")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 80)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info=False, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info=True, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def set_level(self, level: str):
        """
        Set logging level
        
        Args:
            level: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.info(f"Log level set to {level.upper()}")
        else:
            self.warning(f"Invalid log level: {level}")


# Global logger instance
logger = SimulatorLogger()


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"{func_name} completed in {elapsed:.4f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func_name} failed after {elapsed:.4f}s: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_performance(operation_name: str):
    """
    Decorator to log performance of operations
    
    Usage:
        @log_performance("Physics Update")
        def update_physics(dt):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                if elapsed > 0.1:  # Log if operation takes more than 100ms
                    logger.warning(f"{operation_name} took {elapsed:.4f}s (slow)")
                else:
                    logger.debug(f"{operation_name} took {elapsed:.4f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{operation_name} failed after {elapsed:.4f}s: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


class PerformanceTracker:
    """Track performance metrics for the simulator"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start(self, metric_name: str):
        """Start tracking a metric"""
        self.start_times[metric_name] = time.time()
    
    def end(self, metric_name: str):
        """End tracking a metric and record the duration"""
        if metric_name in self.start_times:
            duration = time.time() - self.start_times[metric_name]
            
            if metric_name not in self.metrics:
                self.metrics[metric_name] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
            
            self.metrics[metric_name]['count'] += 1
            self.metrics[metric_name]['total_time'] += duration
            self.metrics[metric_name]['min_time'] = min(self.metrics[metric_name]['min_time'], duration)
            self.metrics[metric_name]['max_time'] = max(self.metrics[metric_name]['max_time'], duration)
            
            del self.start_times[metric_name]
    
    def get_stats(self, metric_name: str) -> dict:
        """Get statistics for a metric"""
        if metric_name in self.metrics:
            m = self.metrics[metric_name]
            return {
                'count': m['count'],
                'total_time': m['total_time'],
                'avg_time': m['total_time'] / m['count'] if m['count'] > 0 else 0,
                'min_time': m['min_time'],
                'max_time': m['max_time']
            }
        return None
    
    def report(self):
        """Generate performance report"""
        logger.info("=" * 80)
        logger.info("Performance Report")
        logger.info("=" * 80)
        
        for metric_name, stats in self.metrics.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            logger.info(f"{metric_name}:")
            logger.info(f"  Count: {stats['count']}")
            logger.info(f"  Total: {stats['total_time']:.4f}s")
            logger.info(f"  Average: {avg_time:.4f}s")
            logger.info(f"  Min: {stats['min_time']:.4f}s")
            logger.info(f"  Max: {stats['max_time']:.4f}s")
        
        logger.info("=" * 80)


# Global performance tracker
perf_tracker = PerformanceTracker()

