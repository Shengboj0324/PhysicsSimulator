"""
Base Controller Interfaces for the Physics Simulator

These abstract base classes define the interfaces that custom controllers must implement.
Users can create their own controllers by inheriting from these base classes.
"""

from abc import ABC, abstractmethod


class BaseRudderController(ABC):
    """
    Abstract base class for rudder controllers.
    
    Rudder controllers determine the rudder angle based on the boat state
    and navigation goals.
    """
    
    def __init__(self, boat):
        """
        Initialize the rudder controller.
        
        Args:
            boat: Reference to the boat object
        """
        self.boat = boat
    
    @abstractmethod
    def calculate_rudder_angle(self, target_heading=None, **kwargs):
        """
        Calculate the desired rudder angle.
        
        Args:
            target_heading: Target heading in degrees (optional)
            **kwargs: Additional parameters specific to the controller
            
        Returns:
            float: Rudder angle in degrees (typically -10 to +10)
        """
        pass
    
    def apply_rudder(self, angle):
        """Apply the rudder angle to the boat."""
        from ...core.Variables import Angle
        # Clamp angle to physical limits
        angle = max(-10, min(10, angle))
        self.boat.hulls[-1].angle = Angle(1, angle)


class BaseSailController(ABC):
    """
    Abstract base class for sail controllers.
    
    Sail controllers determine the sail angle based on wind conditions
    and sailing strategy.
    """
    
    def __init__(self, boat):
        """
        Initialize the sail controller.
        
        Args:
            boat: Reference to the boat object
        """
        self.boat = boat
    
    @abstractmethod
    def calculate_sail_angle(self, apparent_wind_angle, **kwargs):
        """
        Calculate the desired sail angle.
        
        Args:
            apparent_wind_angle: Apparent wind angle relative to boat in degrees
            **kwargs: Additional parameters specific to the controller
            
        Returns:
            float: Sail angle in degrees
        """
        pass
    
    def apply_sail_angle(self, angle):
        """Apply the sail angle to the boat."""
        from ...core.Variables import Angle
        if self.boat.sails:
            self.boat.sails[0].setSailRotation(Angle(1, angle))


class BasePathfindingController(ABC):
    """
    Abstract base class for pathfinding controllers.
    
    Pathfinding controllers determine the route between waypoints,
    handling obstacles like no-go zones.
    """
    
    def __init__(self, boat, controller):
        """
        Initialize the pathfinding controller.
        
        Args:
            boat: Reference to the boat object
            controller: Reference to the main controller (for accessing polars, etc.)
        """
        self.boat = boat
        self.controller = controller
    
    @abstractmethod
    def calculate_path(self, start_point, end_point, wind_direction, **kwargs):
        """
        Calculate a path between two points.
        
        Args:
            start_point: [x, y] starting coordinates
            end_point: [x, y] destination coordinates
            wind_direction: Current wind direction in degrees
            **kwargs: Additional parameters specific to the controller
            
        Returns:
            list: List of [x, y] waypoints defining the path
        """
        pass
    
    @abstractmethod
    def check_waypoint_arrival(self, position, target_waypoint, **kwargs):
        """
        Check if the boat has arrived at a waypoint.
        
        Args:
            position: Current boat position [x, y]
            target_waypoint: Target waypoint [x, y]
            **kwargs: Additional parameters specific to the controller
            
        Returns:
            bool: True if waypoint has been reached
        """
        pass