"""
Custom exceptions for the Physics Sailing Simulator

This module defines all custom exceptions used throughout the simulator,
providing clear error messages and proper exception hierarchy.
"""


class SimulatorError(Exception):
    """Base exception for all simulator errors"""
    pass


class ConfigurationError(SimulatorError):
    """Raised when configuration is invalid or missing"""
    pass


class ValidationError(SimulatorError):
    """Raised when input validation fails"""
    pass


class PhysicsError(SimulatorError):
    """Raised when physics calculations encounter invalid states"""
    pass


class ControlError(SimulatorError):
    """Raised when control system encounters errors"""
    pass


class NavigationError(SimulatorError):
    """Raised when navigation calculations fail"""
    pass


class DataError(SimulatorError):
    """Raised when data loading or parsing fails"""
    pass


class BoatConfigurationError(ConfigurationError):
    """Raised when boat configuration is invalid"""
    pass


class WindConfigurationError(ConfigurationError):
    """Raised when wind configuration is invalid"""
    pass


class PolarDataError(DataError):
    """Raised when polar diagram data is invalid or missing"""
    pass


class FoilDataError(DataError):
    """Raised when foil coefficient data is invalid or missing"""
    pass


class WaypointError(NavigationError):
    """Raised when waypoint data is invalid"""
    pass


class PathfindingError(NavigationError):
    """Raised when pathfinding algorithm fails"""
    pass


class AngleError(ValidationError):
    """Raised when angle values are out of valid range"""
    pass


class VectorError(ValidationError):
    """Raised when vector operations are invalid"""
    pass


class ControllerError(ControlError):
    """Raised when controller encounters an error"""
    pass


class AlgorithmError(ControlError):
    """Raised when control algorithm encounters an error"""
    pass


class DisplayError(SimulatorError):
    """Raised when display system encounters errors"""
    pass


class MapError(SimulatorError):
    """Raised when map data loading or processing fails"""
    pass


class GRIBError(DataError):
    """Raised when GRIB weather data is invalid or unavailable"""
    pass
