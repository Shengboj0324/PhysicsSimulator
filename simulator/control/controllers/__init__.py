"""
Controller module for the Physics Simulator.

This module provides modular controllers for rudder, sail, and pathfinding.
"""

from .base_controllers import (
    BaseRudderController,
    BaseSailController,
    BasePathfindingController
)

from .rudder.simple_rudder import (
    SimpleRudderController,
    WaypointRudderController
)

from .sail.simple_sail import (
    SimpleSailController,
    PolarBasedSailController,
    angle_of_attack
)

from .pathfinding.simple_pathfinding import (
    SimplePathfindingController
)

__all__ = [
    # Base classes
    'BaseRudderController',
    'BaseSailController',  
    'BasePathfindingController',
    
    # Rudder controllers
    'SimpleRudderController',
    'WaypointRudderController',
    
    # Sail controllers
    'SimpleSailController',
    'PolarBasedSailController',
    'angle_of_attack',
    
    # Pathfinding controllers
    'SimplePathfindingController',
]