"""
Input validation utilities for the Physics Sailing Simulator

Provides comprehensive validation for all inputs to ensure data integrity
and prevent errors from propagating through the system.
"""

from typing import Any, List, Tuple, Optional, Union
import math
from pathlib import Path
from .exceptions import (
    ValidationError, AngleError, VectorError, 
    ConfigurationError, WaypointError
)
from .logger import logger


class Validator:
    """Comprehensive validation utilities"""
    
    @staticmethod
    def validate_angle(value: float, name: str = "angle", 
                      min_val: float = -float('inf'), 
                      max_val: float = float('inf')) -> float:
        """
        Validate angle value
        
        Args:
            value: Angle value to validate
            name: Name of the angle for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Validated angle value
            
        Raises:
            AngleError: If validation fails
        """
        if not isinstance(value, (int, float)):
            raise AngleError(f"{name} must be a number, got {type(value)}")
        
        if math.isnan(value):
            raise AngleError(f"{name} cannot be NaN")
        
        if math.isinf(value):
            raise AngleError(f"{name} cannot be infinite")
        
        if value < min_val or value > max_val:
            raise AngleError(
                f"{name} must be between {min_val} and {max_val}, got {value}"
            )
        
        return float(value)
    
    @staticmethod
    def validate_positive(value: float, name: str = "value", 
                         allow_zero: bool = False) -> float:
        """
        Validate that value is positive
        
        Args:
            value: Value to validate
            name: Name for error messages
            allow_zero: Whether to allow zero
            
        Returns:
            Validated value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be a number, got {type(value)}")
        
        if math.isnan(value):
            raise ValidationError(f"{name} cannot be NaN")
        
        if math.isinf(value):
            raise ValidationError(f"{name} cannot be infinite")
        
        if allow_zero:
            if value < 0:
                raise ValidationError(f"{name} must be non-negative, got {value}")
        else:
            if value <= 0:
                raise ValidationError(f"{name} must be positive, got {value}")
        
        return float(value)
    
    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float, 
                      name: str = "value") -> float:
        """
        Validate that value is within range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            name: Name for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be a number, got {type(value)}")
        
        if math.isnan(value):
            raise ValidationError(f"{name} cannot be NaN")
        
        if math.isinf(value):
            raise ValidationError(f"{name} cannot be infinite")
        
        if value < min_val or value > max_val:
            raise ValidationError(
                f"{name} must be between {min_val} and {max_val}, got {value}"
            )
        
        return float(value)
    
    @staticmethod
    def validate_file_exists(filepath: Union[str, Path], 
                           name: str = "file") -> Path:
        """
        Validate that file exists
        
        Args:
            filepath: Path to file
            name: Name for error messages
            
        Returns:
            Path object
            
        Raises:
            ValidationError: If file doesn't exist
        """
        path = Path(filepath)
        
        if not path.exists():
            raise ValidationError(f"{name} does not exist: {filepath}")
        
        if not path.is_file():
            raise ValidationError(f"{name} is not a file: {filepath}")
        
        logger.debug(f"Validated file exists: {filepath}")
        return path
    
    @staticmethod
    def validate_waypoint(waypoint: Any, name: str = "waypoint") -> List[float]:
        """
        Validate waypoint format
        
        Args:
            waypoint: Waypoint to validate (should be [x, y])
            name: Name for error messages
            
        Returns:
            Validated waypoint as [x, y]
            
        Raises:
            WaypointError: If validation fails
        """
        if not isinstance(waypoint, (list, tuple)):
            raise WaypointError(
                f"{name} must be a list or tuple, got {type(waypoint)}"
            )
        
        if len(waypoint) != 2:
            raise WaypointError(
                f"{name} must have exactly 2 coordinates, got {len(waypoint)}"
            )
        
        try:
            x = float(waypoint[0])
            y = float(waypoint[1])
        except (ValueError, TypeError) as e:
            raise WaypointError(f"{name} coordinates must be numbers: {e}")
        
        if math.isnan(x) or math.isnan(y):
            raise WaypointError(f"{name} coordinates cannot be NaN")
        
        if math.isinf(x) or math.isinf(y):
            raise WaypointError(f"{name} coordinates cannot be infinite")
        
        return [x, y]
    
    @staticmethod
    def validate_waypoints(waypoints: List[Any], 
                          min_count: int = 1) -> List[List[float]]:
        """
        Validate list of waypoints
        
        Args:
            waypoints: List of waypoints to validate
            min_count: Minimum number of waypoints required
            
        Returns:
            Validated list of waypoints
            
        Raises:
            WaypointError: If validation fails
        """
        if not isinstance(waypoints, list):
            raise WaypointError(f"Waypoints must be a list, got {type(waypoints)}")
        
        if len(waypoints) < min_count:
            raise WaypointError(
                f"At least {min_count} waypoint(s) required, got {len(waypoints)}"
            )
        
        validated = []
        for i, wp in enumerate(waypoints):
            validated.append(Validator.validate_waypoint(wp, f"waypoint[{i}]"))
        
        logger.debug(f"Validated {len(validated)} waypoints")
        return validated
    
    @staticmethod
    def validate_vector_magnitude(magnitude: float, 
                                  name: str = "magnitude") -> float:
        """
        Validate vector magnitude
        
        Args:
            magnitude: Magnitude to validate
            name: Name for error messages
            
        Returns:
            Validated magnitude
            
        Raises:
            VectorError: If validation fails
        """
        if not isinstance(magnitude, (int, float)):
            raise VectorError(f"{name} must be a number, got {type(magnitude)}")
        
        if math.isnan(magnitude):
            raise VectorError(f"{name} cannot be NaN")
        
        if math.isinf(magnitude):
            raise VectorError(f"{name} cannot be infinite")
        
        if magnitude < 0:
            raise VectorError(f"{name} cannot be negative, got {magnitude}")
        
        return float(magnitude)
    
    @staticmethod
    def validate_config_dict(config: Any, required_keys: List[str], 
                           name: str = "configuration") -> dict:
        """
        Validate configuration dictionary
        
        Args:
            config: Configuration to validate
            required_keys: List of required keys
            name: Name for error messages
            
        Returns:
            Validated configuration
            
        Raises:
            ConfigurationError: If validation fails
        """
        if not isinstance(config, dict):
            raise ConfigurationError(
                f"{name} must be a dictionary, got {type(config)}"
            )
        
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ConfigurationError(
                f"{name} missing required keys: {missing_keys}"
            )
        
        logger.debug(f"Validated configuration: {name}")
        return config
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        Clamp value to range
        
        Args:
            value: Value to clamp
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            Clamped value
        """
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, 
                   default: float = 0.0) -> float:
        """
        Safe division with default value for division by zero
        
        Args:
            numerator: Numerator
            denominator: Denominator
            default: Default value if denominator is zero
            
        Returns:
            Result of division or default value
        """
        if abs(denominator) < 1e-10:  # Avoid division by very small numbers
            logger.warning(f"Division by near-zero: {denominator}, using default {default}")
            return default
        
        return numerator / denominator

