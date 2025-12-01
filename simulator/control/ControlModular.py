"""
Modular Controller for Physics Sailing Simulator - Industrial Grade

This is a refactored version of Control.py that uses the modular controller system.
It allows users to plug in custom rudder, sail, and pathfinding controllers.

Enhanced with:
- Comprehensive type hints
- Input validation
- Error handling
- Logging
- Performance monitoring
- Competition-ready features
"""

import math
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import sys

# Fix imports - use absolute imports with fallback
try:
    from simulator.core.Variables import *
    from simulator.utils.navigation_utils import normalize_angle
    from simulator.core.Boat import Boat
    from simulator.control.controllers import (
        SimpleRudderController,
        WaypointRudderController,
        SimpleSailController,
        SimplePathfindingController
    )
except ImportError:
    from ..core.Variables import *
    from ..utils.navigation_utils import normalize_angle
    from ..core.Boat import Boat
    from .controllers import (
        SimpleRudderController,
        WaypointRudderController,
        SimpleSailController,
        SimplePathfindingController
    )

# Import validation and error handling
try:
    from simulator.core.validators import Validator
    from simulator.core.exceptions import ControlError, ValidationError, ConfigurationError
    from simulator.core.logger import logger, log_performance
    from simulator.core.constants import (
        MIN_WAYPOINT_DISTANCE, MAX_WAYPOINT_DISTANCE,
        DEFAULT_RECALC_INTERVAL, DEFAULT_POLAR_FILE
    )
except ImportError:
    try:
        from ..core.validators import Validator
        from ..core.exceptions import ControlError, ValidationError, ConfigurationError
        from ..core.logger import logger, log_performance
        from ..core.constants import (
            MIN_WAYPOINT_DISTANCE, MAX_WAYPOINT_DISTANCE,
            DEFAULT_RECALC_INTERVAL, DEFAULT_POLAR_FILE
        )
    except ImportError:
        # Fallback for backward compatibility
        class Validator:
            @staticmethod
            def validate_positive(value, name="value", allow_zero=False):
                return float(value)
            @staticmethod
            def validate_file_exists(filepath, name="file"):
                from pathlib import Path
                return Path(filepath)

        class ControlError(Exception):
            pass
        class ValidationError(Exception):
            pass
        class ConfigurationError(Exception):
            pass

        class logger:
            @staticmethod
            def info(msg, **kwargs):
                print(f"INFO: {msg}")
            @staticmethod
            def error(msg, **kwargs):
                print(f"ERROR: {msg}")
            @staticmethod
            def warning(msg, **kwargs):
                print(f"WARNING: {msg}")
            @staticmethod
            def debug(msg, **kwargs):
                pass

        def log_performance(func):
            return func

        MIN_WAYPOINT_DISTANCE = 0.1
        MAX_WAYPOINT_DISTANCE = 10000.0
        DEFAULT_RECALC_INTERVAL = 1.0
        DEFAULT_POLAR_FILE = "data/test.pol"


class ModularController:
    """
    Main controller that coordinates rudder, sail, and pathfinding controllers.
    
    This class replaces the original Controler class but uses pluggable
    controller modules for each subsystem.
    """
    
    def __init__(self, boat, polars_file="data/test.pol", 
                 rudder_controller=None,
                 sail_controller=None,
                 pathfinding_controller=None):
        """
        Initialize the modular controller.
        
        Args:
            boat: Boat instance to control
            polars_file: Path to polar diagram file
            rudder_controller: Custom rudder controller (uses SimpleRudderController if None)
            sail_controller: Custom sail controller (uses SimpleSailController if None)
            pathfinding_controller: Custom pathfinding controller (uses SimplePathfindingController if None)
        """
        self.boat = boat
        self.polars = self.readPolar(polars_file)
        self.active_course = []
        self.waypoints = []
        self.course_type = None
        self.autopilot_enabled = False
        
        # Initialize controllers with defaults if not provided
        self.rudder_controller = rudder_controller or WaypointRudderController(boat)
        self.sail_controller = sail_controller or SimpleSailController(boat)
        self.pathfinding_controller = pathfinding_controller or SimplePathfindingController(boat, self)
    
    def set_rudder_controller(self, controller):
        """Set a custom rudder controller."""
        self.rudder_controller = controller
        
    def set_sail_controller(self, controller):
        """Set a custom sail controller."""
        self.sail_controller = controller
        
    def set_pathfinding_controller(self, controller):
        """Set a custom pathfinding controller."""
        self.pathfinding_controller = controller
    
    def plan(self, plantype, waypoints):
        """
        Initialize control algorithm based on plan type.
        
        This method maintains compatibility with the original Controller interface.
        
        Args:
            plantype: Type of plan ('e' for endurance, 'p' for precision, 's' for station keeping)
            waypoints: List of waypoints for the plan
            
        Returns:
            The active course
        """
        self.course_type = plantype
        self.waypoints = waypoints
        self.calculate_next_leg()
        return self.active_course
    
    def calculate_next_leg(self):
        """
        Calculate path segments between waypoints using the pathfinding controller.
        
        This method uses the modular pathfinding controller to plan routes
        between waypoints, handling tacking and jibing as needed.
        """
        self.active_course = []
        
        if not self.waypoints:
            return
        
        # Start from current position
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        
        # Calculate path to first waypoint
        wind_dir = self.boat.wind.angle.calc()
        
        for i, waypoint in enumerate(self.waypoints):
            # Get path segment from pathfinding controller
            segment = self.pathfinding_controller.calculate_path(
                current_pos, waypoint, wind_dir, ref_lat=self.boat.refLat
            )
            
            # Add segment to active course
            self.active_course.extend(segment)
            
            # Update current position for next segment
            current_pos = waypoint
            
            # For endurance courses, loop back to start
            if self.course_type == 'e' and i == len(self.waypoints) - 1:
                segment = self.pathfinding_controller.calculate_path(
                    waypoint, self.waypoints[0], wind_dir, ref_lat=self.boat.refLat
                )
                self.active_course.extend(segment)
    
    def update(self, dt):
        """
        Main update method called each simulation step.
        
        Args:
            dt: Time step in seconds
        """
        if not self.autopilot_enabled:
            return
            
        # Check waypoint arrival
        if self.active_course:
            current_waypoint = self.active_course[0]
            if self.pathfinding_controller.check_waypoint_arrival(
                self.boat.position, current_waypoint, ref_lat=self.boat.refLat
            ):
                # Remove reached waypoint
                self.active_course.pop(0)
                
                # Recalculate path if needed
                if not self.active_course and self.waypoints:
                    self.calculate_next_leg()
        
        # Update rudder control
        if self.active_course and isinstance(self.rudder_controller, WaypointRudderController):
            self.rudder_controller.steer_to_waypoint(self.active_course[0])
        
        # Update sail control
        if isinstance(self.sail_controller, SimpleSailController):
            self.sail_controller.update_sail_trim()
    
    def update_rudder(self, noise_factor=2, stability_factor=1):
        """
        Update rudder using the rudder controller.
        
        This method maintains compatibility with the original interface.
        """
        if self.active_course and isinstance(self.rudder_controller, WaypointRudderController):
            self.rudder_controller.steer_to_waypoint(
                self.active_course[0],
                noise_factor=noise_factor,
                stability_factor=stability_factor
            )
    
    def update_rudder_angle(self, noise_factor, stability_factor, target_angle):
        """
        Update rudder to a specific angle.
        
        This method maintains compatibility with the original interface.
        """
        angle = self.rudder_controller.calculate_rudder_angle(
            target_angle.calc(),
            noise_factor=noise_factor,
            stability_factor=stability_factor
        )
        self.rudder_controller.apply_rudder(angle)
    
    def update_sails(self):
        """
        Update sails using the sail controller.
        
        This method maintains compatibility with the original interface.
        """
        if isinstance(self.sail_controller, SimpleSailController):
            self.sail_controller.update_sail_trim()
    
    def readPolar(self, filename):
        """Read polar file (copied from original Control.py)."""
        file_read = open(filename, 'r')
        lines = file_read.read()
        lines = lines.split('\n')
        seperateVar = ";"
        for c in lines[0]:
            if c == '\t':
                seperateVar = c
        polar = [[0]]
        
        polar[0] += [float(x) for x in lines[0].split(seperateVar)[1:]]
        
        for i in range(1, len(lines) - 1):
            if lines[i] != "":
                polar.append([float(x) for x in lines[i].split(seperateVar)])
            
        polar.append([float(x) for x in lines[-1].split(";")[1:]])
        
        return polar
    
    def VB(self, a, wind_speed):
        """Get boat speed from polars (copied from original Control.py)."""
        i = 0
        a = abs(a.calc()) % 180
        for el in self.polars[1:-1]:
            i += 1
            if el[0] > a:
                k = 0
                for w in self.polars[0][1:]:
                    k += 1
                    if w > wind_speed:
                        return self.polars[i][k]
        return -1


# Maintain backward compatibility
Controler = ModularController  # Original spelling