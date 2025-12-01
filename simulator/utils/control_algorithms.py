"""
Control Algorithms Module - Industrial Grade

Base classes and implementations for control algorithms.

Enhanced with:
- Comprehensive type hints
- Input validation
- Error handling
- Logging
- Performance monitoring
- Competition-ready features
"""

from abc import ABC, abstractmethod
import math
from typing import List, Tuple, Optional, Dict, Any
import sys

# Fix imports - use EXPLICIT imports (NO WILDCARDS!)
try:
    from simulator.core.Variables import (
        Angle, Vector, degree2meter, meter2degreeX, meter2degreeY
    )
    from simulator.utils.station_keeping import StationKeepingController
except ImportError:
    from ..core.Variables import (
        Angle, Vector, degree2meter, meter2degreeX, meter2degreeY
    )
    from .station_keeping import StationKeepingController

# Import validation and error handling
try:
    from simulator.core.validators import Validator
    from simulator.core.exceptions import ControlError, ValidationError
    from simulator.core.logger import logger, log_performance
    from simulator.core.constants import (
        MIN_WAYPOINT_DISTANCE, MAX_WAYPOINT_DISTANCE,
        DEFAULT_RECALC_INTERVAL
    )
except ImportError:
    try:
        from ..core.validators import Validator
        from ..core.exceptions import ControlError, ValidationError
        from ..core.logger import logger, log_performance
        from ..core.constants import (
            MIN_WAYPOINT_DISTANCE, MAX_WAYPOINT_DISTANCE,
            DEFAULT_RECALC_INTERVAL
        )
    except ImportError:
        # Fallback for backward compatibility
        class Validator:
            @staticmethod
            def validate_positive(value, name="value", allow_zero=False):
                return float(value)
            @staticmethod
            def validate_range(value, min_val, max_val, name="value"):
                return float(value)

        class ControlError(Exception):
            pass
        class ValidationError(Exception):
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

# CONSTANTS - NO MAGIC NUMBERS!
WAYPOINT_ARRIVAL_RADIUS = 5.0  # meters
DEFAULT_RECALC_INTERVAL = 1.0  # seconds
MAX_STUCK_ITERATIONS = 100  # iterations before skipping waypoint
VMG_OPTIMIZATION_INTERVAL = 2.0  # seconds
VMG_HEADING_SEARCH_MIN = -90  # degrees
VMG_HEADING_SEARCH_MAX = 90  # degrees
VMG_HEADING_SEARCH_STEP = 5  # degrees


class ControlAlgorithm(ABC):
    """
    Base class for all control algorithms - BULLETPROOF VERSION

    All algorithm implementations must inherit from this class and implement
    the update() and get_state_info() methods.
    """

    def __init__(self, boat, controller):
        """
        Initialize control algorithm with validation

        Args:
            boat: Boat instance to control
            controller: Controller instance

        Raises:
            ValidationError: If boat or controller is invalid
        """
        if boat is None:
            raise ValidationError("Boat instance cannot be None")
        if controller is None:
            raise ValidationError("Controller instance cannot be None")

        self.boat = boat
        self.controller = controller

        logger.debug(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update control logic - must be implemented by subclasses

        Args:
            dt: Time step in seconds
        """
        pass

    @abstractmethod
    def get_state_info(self) -> Dict[str, Any]:
        """
        Get current state information for debugging

        Returns:
            Dictionary with algorithm state information
        """
        pass


class WaypointFollowingAlgorithm(ControlAlgorithm):
    """
    Standard waypoint following control algorithm - BULLETPROOF VERSION

    Follows a series of waypoints with automatic path recalculation and
    stuck detection to prevent infinite loops.
    """

    def __init__(self, boat, controller, waypoints: List[List[float]], course_type: str):
        """
        Initialize waypoint following algorithm with EXTREME validation

        Args:
            boat: Boat instance
            controller: Controller instance
            waypoints: List of [x, y] waypoint coordinates
            course_type: Course type ('e'=endurance, 'p'=precision, 's'=station keeping)

        Raises:
            ValidationError: If waypoints or course_type is invalid
        """
        super().__init__(boat, controller)

        # Validate waypoints
        if not waypoints or len(waypoints) == 0:
            raise ValidationError("Waypoints list cannot be empty")

        if not isinstance(waypoints, list):
            raise ValidationError(f"Waypoints must be a list, got {type(waypoints)}")

        for i, wp in enumerate(waypoints):
            if not isinstance(wp, (list, tuple)) or len(wp) < 2:
                raise ValidationError(f"Waypoint {i} must be [x, y] coordinates, got {wp}")
            try:
                float(wp[0])
                float(wp[1])
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Waypoint {i} coordinates must be numeric: {e}")

        # Validate course_type
        if course_type not in ['e', 'p', 's']:
            raise ValidationError(
                f"Invalid course_type: '{course_type}'. Must be 'e', 'p', or 's'"
            )

        self.waypoints = waypoints
        self.course_type = course_type
        self.current_target_idx = 0
        self.active_course: List[List[float]] = []
        self.last_recalc_time = 0.0
        self.recalc_interval = DEFAULT_RECALC_INTERVAL
        self.stuck_counter = 0  # Prevent infinite loops

        logger.info(
            f"WaypointFollowingAlgorithm initialized: "
            f"{len(waypoints)} waypoints, course_type='{course_type}'"
        )
        
    def update(self, dt: float) -> None:
        """
        Update waypoint following logic - BULLETPROOF VERSION

        Args:
            dt: Time step in seconds
        """
        try:
            # Validate input
            if dt is None or dt < 0 or math.isnan(dt) or math.isinf(dt):
                logger.warning(f"Invalid dt: {dt}, using 0.0")
                dt = 0.0

            if self.target_reached():
                # Reset stuck counter on success
                self.stuck_counter = 0

                if self.course_type == "e" and self.current_target_idx >= len(self.waypoints) - 1:
                    self.current_target_idx = 0
                    logger.info("Completed lap, continuing endurance course")
                else:
                    self.current_target_idx += 1
                    logger.info(f"Moving to waypoint {self.current_target_idx}")

                self.calculate_next_legs()
                self.last_recalc_time = 0
            else:
                # Check if stuck (waypoint unreachable)
                self.stuck_counter += 1
                if self.stuck_counter > MAX_STUCK_ITERATIONS:
                    logger.error(
                        f"Waypoint {self.current_target_idx} unreachable after "
                        f"{MAX_STUCK_ITERATIONS} iterations, skipping"
                    )
                    self.current_target_idx += 1
                    self.stuck_counter = 0

                    # Bounds check
                    if self.current_target_idx >= len(self.waypoints):
                        if self.course_type == "e":
                            self.current_target_idx = 0
                        else:
                            logger.warning("All waypoints completed or unreachable")
                            return

                    self.calculate_next_legs()

            self.last_recalc_time += dt
            if self.last_recalc_time >= self.recalc_interval:
                self.recalculate_current_leg()
                self.last_recalc_time = 0

            self.controller.updateRudder(2, 1)
            self.controller.updateSails()

        except Exception as e:
            logger.error(f"Error in waypoint following update: {e}", exc_info=True)
            # Graceful degradation: maintain current course
        
    def target_reached(self) -> bool:
        """
        Check if current target waypoint has been reached - BULLETPROOF VERSION

        Returns:
            True if within WAYPOINT_ARRIVAL_RADIUS of target, False otherwise
        """
        try:
            if self.current_target_idx >= len(self.waypoints) and self.course_type != "e":
                return False

            # Bounds check
            if not self.waypoints or len(self.waypoints) == 0:
                logger.error("No waypoints available")
                return False

            current_target = self.waypoints[self.current_target_idx % len(self.waypoints)]
            current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]

            dx = current_target[0] - current_pos[0]
            dy = current_target[1] - current_pos[1]
            dist = degree2meter(math.sqrt(dx**2 + dy**2))

            if dist < WAYPOINT_ARRIVAL_RADIUS:
                logger.info(
                    f"Reached waypoint {self.current_target_idx % len(self.waypoints)}, "
                    f"distance={dist:.2f}m"
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Error checking target reached: {e}", exc_info=True)
            return False
        
    def calculate_next_legs(self):
        """Calculate next two legs of the course"""
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        
        self.active_course = [current_pos]
        
        if self.current_target_idx < len(self.waypoints):
            next_target = self.waypoints[self.current_target_idx % len(self.waypoints)]
            next_leg = self.controller.leg(self.active_course[-1], next_target)
            self.active_course.extend(next_leg)
            
            if self.course_type == "e" and self.current_target_idx == len(self.waypoints) - 1:
                next_leg = self.controller.leg(self.active_course[-1], self.waypoints[0])
            elif self.current_target_idx + 1 < len(self.waypoints):
                next_leg = self.controller.leg(self.active_course[-1], 
                                             self.waypoints[(self.current_target_idx + 1) % len(self.waypoints)])
            else:
                next_leg = []
            
            self.active_course.extend(next_leg)
        
        self.controller.active_course = self.active_course
        
        if hasattr(self.controller, 'display'):
            self.controller.display.clear_paths()
            self.controller.display.boat.plotCourse(self.active_course, 'green')
            
    def recalculate_current_leg(self) -> None:
        """
        Recalculate path to current target - BULLETPROOF VERSION
        """
        try:
            if self.current_target_idx >= len(self.waypoints):
                logger.debug("No more waypoints to recalculate")
                return

            current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
            target_waypoint = self.waypoints[self.current_target_idx]

            logger.debug(f"Recalculating path to waypoint {self.current_target_idx}: {target_waypoint}")

            new_leg = self.controller.leg(current_pos, target_waypoint)

            self.active_course = [current_pos]
            if isinstance(new_leg, list):
                self.active_course.extend(new_leg)

            self.controller.active_course = self.active_course

            if hasattr(self.controller, 'display') and self.controller.display is not None:
                try:
                    self.controller.display.clear_paths()
                    self.controller.display.boat.plotCourse(self.active_course, 'green')
                except Exception as e:
                    logger.warning(f"Failed to update display: {e}")

        except Exception as e:
            logger.error(f"Error recalculating current leg: {e}", exc_info=True)
            
    def get_state_info(self):
        """Get current algorithm state"""
        return {
            "algorithm": "Waypoint Following",
            "current_target": self.current_target_idx,
            "total_waypoints": len(self.waypoints),
            "course_type": self.course_type
        }


class StationKeepingAlgorithm(ControlAlgorithm):
    """Station keeping control algorithm"""
    
    def __init__(self, boat, controller, waypoints):
        super().__init__(boat, controller)
        self.station_keeper = StationKeepingController(
            boat, 
            waypoints, 
            controller,
            controller.display.clear_paths if hasattr(controller, 'display') else None
        )
        
        current_pos = [boat.position.xcomp(), boat.position.ycomp()]
        self.controller.active_course = [current_pos] + controller.leg(current_pos, self.station_keeper.upwind_target)
        
    def update(self, dt):
        """Delegate to station keeper"""
        self.station_keeper.update(dt)
        
    def get_state_info(self):
        """Get current algorithm state"""
        return {
            "algorithm": "Station Keeping",
            "state": self.station_keeper.state if hasattr(self.station_keeper, 'state') else "Unknown"
        }


class DirectControlAlgorithm(ControlAlgorithm):
    """Direct control algorithm for manual sailing"""
    
    def __init__(self, boat, controller):
        super().__init__(boat, controller)
        self.target_heading = None
        
    def set_target_heading(self, heading):
        """Set target heading in degrees"""
        self.target_heading = heading
        
    def update(self, dt):
        """Update direct control"""
        if self.target_heading is not None:
            target_angle = Angle(1, self.target_heading)
            self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def get_state_info(self):
        """Get current algorithm state"""
        return {
            "algorithm": "Direct Control",
            "target_heading": self.target_heading
        }


class VMGOptimizationAlgorithm(ControlAlgorithm):
    """
    Velocity Made Good optimization algorithm - BULLETPROOF VERSION

    Optimizes heading to maximize velocity made good toward target point.
    """

    def __init__(self, boat, controller, target_point: List[float]):
        """
        Initialize VMG optimization algorithm

        Args:
            boat: Boat instance
            controller: Controller instance
            target_point: Target [x, y] coordinates

        Raises:
            ValidationError: If target_point is invalid
        """
        super().__init__(boat, controller)

        # Validate target_point
        if not target_point or len(target_point) < 2:
            raise ValidationError(f"target_point must be [x, y] coordinates, got {target_point}")

        try:
            float(target_point[0])
            float(target_point[1])
        except (ValueError, TypeError) as e:
            raise ValidationError(f"target_point coordinates must be numeric: {e}")

        self.target_point = target_point
        self.optimization_interval = VMG_OPTIMIZATION_INTERVAL
        self.last_optimization_time = 0.0
        self.current_heading: Optional[float] = None

        logger.info(f"VMGOptimizationAlgorithm initialized: target={target_point}")
        
    def update(self, dt):
        """Update VMG optimization"""
        self.last_optimization_time += dt
        
        if self.last_optimization_time >= self.optimization_interval:
            self.optimize_heading()
            self.last_optimization_time = 0
            
        if self.current_heading is not None:
            target_angle = Angle(1, self.current_heading)
            self.controller.updateRudderAngle(2, 1, target_angle)
            
        self.controller.updateSails()
        
    def optimize_heading(self) -> None:
        """
        Find optimal heading for best VMG to target - BULLETPROOF VERSION
        """
        try:
            current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]

            dx = self.target_point[0] - current_pos[0]
            dy = self.target_point[1] - current_pos[1]
            target_bearing = math.atan2(dy, dx) * 180 / math.pi

            wind_angle = self.boat.wind.angle.calc()
            if wind_angle is None or math.isnan(wind_angle):
                logger.error(f"Invalid wind angle: {wind_angle}")
                return

            relative_wind = normalize_angle_180(wind_angle - self.boat.angle.calc())

            best_vmg = -float('inf')
            best_heading = target_bearing

            # Search for optimal heading
            for heading_offset in range(
                VMG_HEADING_SEARCH_MIN,
                VMG_HEADING_SEARCH_MAX + 1,
                VMG_HEADING_SEARCH_STEP
            ):
                test_heading = target_bearing + heading_offset
                relative_wind_at_heading = normalize_angle_180(wind_angle - test_heading)

                boat_speed = self.controller.VB(Angle(1, abs(relative_wind_at_heading)), self.boat.wind.norm)
                if boat_speed > 0:
                    vmg = boat_speed * math.cos(math.radians(heading_offset))
                    if vmg > best_vmg:
                        best_vmg = vmg
                        best_heading = test_heading

            self.current_heading = best_heading
            logger.info(f"Optimized heading: {best_heading:.1f}° for VMG: {best_vmg:.2f}")

        except Exception as e:
            logger.error(f"Error optimizing heading: {e}", exc_info=True)
        
    def get_state_info(self):
        """Get current algorithm state"""
        return {
            "algorithm": "VMG Optimization",
            "target": self.target_point,
            "current_heading": self.current_heading
        }


def normalize_angle_180(angle: float) -> float:
    """
    Normalize angle to [-180, 180] range - BULLETPROOF VERSION

    Args:
        angle: Angle in degrees

    Returns:
        Normalized angle in [-180, 180] range
    """
    if angle is None:
        logger.warning("normalize_angle_180 called with None, returning 0")
        return 0.0

    if math.isnan(angle) or math.isinf(angle):
        logger.warning(f"normalize_angle_180 called with invalid value: {angle}, returning 0")
        return 0.0

    angle = angle % 360
    if angle > 180:
        angle = angle - 360
    return angle


# Backward compatibility alias
def printA(x):
    """Deprecated: Use normalize_angle_180 instead"""
    return normalize_angle_180(x)