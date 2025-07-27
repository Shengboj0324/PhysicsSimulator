"""
Physics Sailing Simulator

A modular sailing simulator with pluggable controllers for rudder, sail, and pathfinding.
"""

__version__ = "2.0.0"
__author__ = "Noah Potischman"

# Import main components for easy access
from .core.Variables import Angle, Vector
from .core.Boat import Boat
from .core.Foil import foil, Winch
from .display.Display import display
from .control.ControlModular import ModularController

__all__ = [
    'Angle', 'Vector', 'Boat', 'foil', 'Winch', 
    'display', 'ModularController'
]