"""
Main Controller for Physics Sailing Simulator

Manages different control algorithms for waypoint following, station keeping,
and VMG optimization.

Enhanced with type hints, validation, and error handling.
"""

import math
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from ..core.Variables import Angle, Vector
from ..utils.control_algorithms import (
    ControlAlgorithm,
    WaypointFollowingAlgorithm,
    StationKeepingAlgorithm,
    DirectControlAlgorithm,
    VMGOptimizationAlgorithm
)
from ..utils.navigation_utils import normalize_angle, angle_of_attack

# Import validation and error handling
try:
    from ..core.validators import Validator
    from ..core.exceptions import ControlError, ValidationError, ConfigurationError
    from ..core.constants import (
        DEFAULT_WAYPOINT_ARRIVAL_RADIUS,
        DEFAULT_RUDDER_MAX_ANGLE,
        UPWIND_NO_GO_ANGLE,
        DOWNWIND_NO_GO_ANGLE
    )
    from ..core.logger import logger
except ImportError:
    # Fallback for backward compatibility
    class Validator:
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

    DEFAULT_WAYPOINT_ARRIVAL_RADIUS = 5.0
    DEFAULT_RUDDER_MAX_ANGLE = 45.0
    UPWIND_NO_GO_ANGLE = 45.0
    DOWNWIND_NO_GO_ANGLE = 45.0

    class logger:
        @staticmethod
        def info(msg, **kwargs):
            pass
        @staticmethod
        def debug(msg, **kwargs):
            pass
        @staticmethod
        def warning(msg, **kwargs):
            pass
        @staticmethod
        def error(msg, **kwargs):
            pass

# Navigation utility functions moved to navigation_utils.py
printA = normalize_angle  # Alias for backward compatibility
aoa = angle_of_attack    # Alias for backward compatibility


class Controller:
    """
    Main controller that manages different control algorithms

    Note: This class was previously named 'Controler' (typo fixed)
    """

    def __init__(self, boat, polars: str = "data/test.pol"):
        """
        Initialize controller

        Args:
            boat: Boat instance to control
            polars: Path to polar diagram file

        Raises:
            ConfigurationError: If polar file cannot be loaded
        """
        try:
            self.boat = boat
            self.polars = self.readPolar(polars)
            self.active_course: List[List[float]] = []
            self.current_algorithm: Optional[ControlAlgorithm] = None
            self.display = None

            logger.info(f"Controller initialized with polars from {polars}")

        except Exception as e:
            raise ConfigurationError(f"Failed to initialize controller: {e}")

    def plan(self, plantype: str, waypoints: List[List[float]]) -> List[List[float]]:
        """
        Initialize control algorithm based on plan type

        Args:
            plantype: Type of plan ('e' for endurance, 'p' for precision, 's' for station keeping)
            waypoints: List of [lat, lon] waypoint coordinates

        Returns:
            Active course with intermediate waypoints

        Raises:
            ValidationError: If plan type or waypoints are invalid
            ControlError: If algorithm initialization fails
        """
        try:
            # Validate inputs
            if not plantype or plantype not in ['e', 'p', 's']:
                raise ValidationError(f"Invalid plan type: {plantype}. Must be 'e', 'p', or 's'")

            if not waypoints or len(waypoints) == 0:
                raise ValidationError("Waypoints list cannot be empty")

            # Initialize appropriate algorithm
            if plantype in ["e", "p"]:  # endurance or precision
                self.current_algorithm = WaypointFollowingAlgorithm(
                    self.boat, self, waypoints, plantype
                )
                self.current_algorithm.calculate_next_legs()
                logger.info(f"Initialized waypoint following algorithm ({plantype}) with {len(waypoints)} waypoints")

            elif plantype == "s":  # station keeping
                self.current_algorithm = StationKeepingAlgorithm(
                    self.boat, self, waypoints
                )
                logger.info(f"Initialized station keeping algorithm with {len(waypoints)} boundary points")

            return self.active_course

        except Exception as e:
            logger.error(f"Failed to initialize plan: {e}", exc_info=True)
            raise ControlError(f"Plan initialization failed: {e}")

    def set_algorithm(self, algorithm: ControlAlgorithm) -> None:
        """
        Set a custom control algorithm

        Args:
            algorithm: Custom control algorithm instance

        Raises:
            ValidationError: If algorithm is not a ControlAlgorithm instance
        """
        if not isinstance(algorithm, ControlAlgorithm):
            raise ValidationError("Algorithm must be a ControlAlgorithm instance")

        self.current_algorithm = algorithm
        logger.info(f"Set custom algorithm: {algorithm.__class__.__name__}")

    def leg(self, start: List[float], stop: List[float]) -> List[List[float]]:
        """
        Calculate path between two points, handling no-go zones

        Args:
            start: Starting position [lat, lon]
            stop: Target position [lat, lon]

        Returns:
            List of waypoints including intermediate tacking/jibing points
        """
        try:
            # Calculate direct course
            dx = stop[0] - start[0]
            dy = stop[1] - start[1]
            course_angle = Angle(1, math.atan2(dy, dx) * 180 / math.pi)
            distance = math.sqrt(dx * dx + dy * dy)

            # Get wind angles
            global_wind = self.boat.wind.angle.calc()
            boat_heading = self.boat.angle.calc()
            relative_wind = normalize_angle(global_wind - boat_heading)

            # Calculate course relative to wind
            relative_course = normalize_angle(course_angle.calc() - boat_heading)
            angle_to_wind = abs(normalize_angle(relative_course - relative_wind))
            if angle_to_wind > 180:
                angle_to_wind = 360 - angle_to_wind

            # Get no-go zones from polars
            if self.polars and len(self.polars) > 0:
                upwind_nogo = self.polars[-1][0]
                downwind_nogo = 180 - self.polars[-1][1]
            else:
                # Use default no-go zones if polars not available
                upwind_nogo = UPWIND_NO_GO_ANGLE
                downwind_nogo = DOWNWIND_NO_GO_ANGLE
                logger.warning("Using default no-go zones")

            # Check if we need to tack (upwind)
            if angle_to_wind < upwind_nogo:
                logger.debug(f"Tacking required: angle to wind {angle_to_wind:.1f}° < {upwind_nogo:.1f}°")
                return self._calculate_tacking_path(
                    start, stop, relative_wind,
                    boat_heading, upwind_nogo,
                    course_angle, distance
                )

            # Check if we need to jibe (downwind)
            elif (180 - angle_to_wind) < downwind_nogo:
                logger.debug(f"Jibing required: downwind angle {180 - angle_to_wind:.1f}° < {downwind_nogo:.1f}°")
                return self._calculate_jibing_path(
                    start, stop, relative_wind,
                    boat_heading, downwind_nogo,
                    course_angle, distance
                )

            # Direct course is possible
            logger.debug(f"Direct course possible: angle to wind {angle_to_wind:.1f}°")
            return [stop]

        except Exception as e:
            logger.error(f"Error calculating leg: {e}", exc_info=True)
            # Return direct path as fallback
            return [stop]

    def _calculate_tacking_path(self, start, stop, relative_wind, boat_heading,
                               upwind_nogo, course_angle, distance):
        """Calculate tacking path to avoid upwind no-go zone"""
        # Calculate tack angles in boat reference frame
        tack_angle1 = relative_wind + upwind_nogo
        tack_angle2 = relative_wind - upwind_nogo

        # Convert to global coordinates
        global_tack1 = (tack_angle1 + boat_heading) % 360
        global_tack2 = (tack_angle2 + boat_heading) % 360

        # Create vectors for both tack directions
        k = Vector(Angle(1, global_tack1), 1)
        j = Vector(Angle(1, global_tack2), 1)
        v = Vector(course_angle, distance)

        # Calculate intersection point using linear algebra
        D = np.linalg.det(np.array([[k.xcomp(), j.xcomp()],
                                    [k.ycomp(), j.ycomp()]]))
        Dk = np.linalg.det(np.array([[v.xcomp(), j.xcomp()],
                                     [v.ycomp(), j.ycomp()]]))
        Dj = np.linalg.det(np.array([[k.xcomp(), v.xcomp()],
                                     [k.ycomp(), v.ycomp()]]))

        a = Dk/D
        b = Dj/D
        k.norm *= a
        j.norm *= b

        # Return path with intermediate tacking point
        intermediate = [start[0] + k.xcomp(), start[1] + k.ycomp()]
        return [intermediate, stop]

    def _calculate_jibing_path(self, start, stop, relative_wind, boat_heading,
                              downwind_nogo, course_angle, distance):
        """Calculate jibing path to avoid downwind no-go zone"""
        # Calculate jibe angles in boat reference frame
        jibe_angle1 = relative_wind + 180 + downwind_nogo
        jibe_angle2 = relative_wind + 180 - downwind_nogo

        # Convert to global coordinates
        global_jibe1 = (jibe_angle1 + boat_heading) % 360
        global_jibe2 = (jibe_angle2 + boat_heading) % 360

        # Create vectors for both jibe directions
        k = Vector(Angle(1, global_jibe1), 1)
        j = Vector(Angle(1, global_jibe2), 1)
        v = Vector(course_angle, distance)

        # Calculate intersection point using linear algebra
        D = np.linalg.det(np.array([[k.xcomp(), j.xcomp()],
                                    [k.ycomp(), j.ycomp()]]))
        Dk = np.linalg.det(np.array([[v.xcomp(), j.xcomp()],
                                     [v.ycomp(), j.ycomp()]]))
        Dj = np.linalg.det(np.array([[k.xcomp(), v.xcomp()],
                                     [k.ycomp(), v.ycomp()]]))

        a = Dk/D
        b = Dj/D
        k.norm *= a
        j.norm *= b

        # Return path with intermediate jibing point
        intermediate = [start[0] + k.xcomp(), start[1] + k.ycomp()]
        return [intermediate, stop]

    # NOTE: I've desided using best course to next mark while probably the optimal solution brings in a level of complexity that we do not
    # have the time to handle, thus we'll be simplifying.
    # def BestCNM(self, angle, wind): # best course to next mark
    #     # angle is relative to wind
    #     ma = 0
    #     mcnm = 0
    #     for a in range(-180,180):
    #         l = self.VB(Angle(1,a), wind)
    #         CNM = Vector(Angle(1,a),l) * Vector(angle,l)
    #         if mcnm < CNM:
    #             ma = a
    #             mcnm = CNM
    #     axis  = printA(angle.calc())
    #     return [ma,ma-(ma - axis)*2]


    def VB(self,angle, wind): # reading boat polars
        angle =abs(angle.calc())
        angle %= 180
        for i, a in enumerate(self.polars[1:-1]):
            if a[0] > angle:
                for j, s in enumerate(self.polars[0][1:]):
                    if s > wind:
                        return self.polars[i+1][j+1] #TODO add interpolation
        return -1


    def readPolar(self,polar):
        rtn =[]
        text = open(polar).read().split('\n')
        c = "\t"
        if text[0].find(";") != -1:
            c = ";"
        rtn.append([0]+[float(x) for x in text[0].split(c)[1:]])
        for i in text[1:-1]:
            if i.split(c)[0] != '':
                rtn.append([float(x) for x in i.split(c)])
        rtn.append([float(x) for x in text[-1].split(";")[1:]])
        # print(rtn) # prints a list corresponding to a boat angle relative to wind of lists of speeds corresponding to wind speeds
        return rtn

    def update(self, dt, rNoise=2, stability=1):
        """Main update loop delegating to current algorithm"""
        if self.current_algorithm:
            self.current_algorithm.update(dt)
        else:
            # Default behavior when no algorithm is set
            self.updateRudder(rNoise, stability)
            self.updateSails()

    def _check_if_jibing_needed(self, angle1, angle2):
        """Check if path crosses downwind line requiring a jibe"""
        a1 = Angle.norm(angle1).calc()
        a2 = Angle.norm(angle2).calc()

        # Get relative wind
        global_wind = self.boat.wind.angle.calc()
        boat_heading = self.boat.angle.calc()
        relative_wind = normalize_angle(global_wind - boat_heading)

        # Downwind is 180° from wind
        downwind_direction = normalize_angle(relative_wind + 180)

        # Check if we cross the downwind line
        return self._angles_bracket(a1, a2, downwind_direction)

    def _check_if_tacking_needed(self, angle1, angle2):
        """Check if path crosses upwind line requiring a tack"""
        a1 = Angle.norm(angle1).calc()
        a2 = Angle.norm(angle2).calc()

        # Get relative wind
        global_wind = self.boat.wind.angle.calc()
        boat_heading = self.boat.angle.calc()
        relative_wind = normalize_angle(global_wind - boat_heading)

        # Check if we cross the upwind line
        return self._angles_bracket(a1, a2, relative_wind)

    def _angles_bracket(self, a1, a2, target):
        """Check if target angle is between a1 and a2"""
        # Handle angle wraparound
        if a1 <= a2:
            return a1 <= target <= a2
        else:
            return target >= a1 or target <= a2

    def check_waypoint_arrival(self):
        """Check if boat has reached next waypoint and handle transitions"""
        if not self.active_course or len(self.active_course) < 2:
            current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
            self.active_course = [current_pos, current_pos]
            return 0

        arrival_radius = 5  # meters

        # Calculate distance to next waypoint
        dx = self.boat.position.xcomp() - self.active_course[0][0]
        dy = self.boat.position.ycomp() - self.active_course[0][1]
        dist = degree2meter(math.sqrt(dx**2 + dy**2))

        if dist < arrival_radius:
            # Calculate approach and departure angles
            approach_angle = Angle(1, math.atan2(dy, dx) * 180/math.pi)

            if len(self.active_course) > 1:
                next_dx = self.active_course[1][0] - self.active_course[0][0]
                next_dy = self.active_course[1][1] - self.active_course[0][1]
                departure_angle = Angle(1, math.atan2(next_dy, next_dx) * 180/math.pi)
            else:
                departure_angle = approach_angle

            # Remove reached waypoint
            self.active_course.pop(0)

            # Ensure we always have at least 2 points
            if len(self.active_course) == 1:
                self.active_course.append(self.active_course[0])

            # Check if maneuver is needed
            if self._check_if_jibing_needed(approach_angle, departure_angle):
                return 1  # Jibe needed
            if self._check_if_tacking_needed(approach_angle, departure_angle):
                return 2  # Tack needed

        return 0  # No special maneuver needed

    def get_algorithm_info(self):
        """Get information about current control algorithm"""
        if self.current_algorithm:
            return self.current_algorithm.get_state_info()
        return {"algorithm": "None", "state": "No algorithm set"}

    def updateRudder(self, noise_factor=2, stability=1):
        """Update rudder angle to steer toward next waypoint"""
        # Ensure we have a valid course
        if not self.active_course or len(self.active_course) < 2:
            current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
            self.active_course = [current_pos, current_pos]

        # Check for waypoint arrival
        self.check_waypoint_arrival()

        # Calculate steering angle to next waypoint
        dx = self.active_course[0][0] - self.boat.position.xcomp()
        dy = self.active_course[0][1] - self.boat.position.ycomp()
        target_angle = Angle(1, math.atan2(dy, dx) * 180 / math.pi)

        self._apply_rudder_control(target_angle, noise_factor, stability)

    def updateRudderAngle(self, noise_factor, stability, target_angle):
        """Update rudder to steer toward a specific angle"""
        self._apply_rudder_control(target_angle, noise_factor, stability)

    def _apply_rudder_control(self, target_angle, noise_factor, stability):
        """Apply rudder control law to reach target angle"""
        # Calculate heading error
        current_angle = self.boat.linearVelocity.angle
        heading_error = normalize_angle((target_angle - current_angle).calc())

        # Get rotational velocity in degrees/timestep
        rot_velocity = self.boat.rotationalVelocity * 180/math.pi * 0.03

        # Control law: combines heading error with damping
        # - heading_error/40: Normalized error (40° scaling factor)
        # - rot_velocity/stability: Damping term
        # - atan: Smooth saturation function
        # - 2/π: Normalize output to [-1, 1]
        control_signal = 2/math.pi * math.atan(heading_error/40 - rot_velocity/stability)

        # Apply to rudder with physical constraints (-10° to +10°)
        self.boat.hulls[-1].angle = Angle(1, -10 * control_signal * noise_factor)

    def updateSails(self):
        """Update sail angle based on apparent wind"""
        # Get apparent wind angle relative to boat
        apparent_wind = self.boat.globalAparentWind().angle
        apparent_wind += Angle(1, 180)  # Convert to angle wind is coming FROM
        relative_wind = apparent_wind - self.boat.angle

        # Set sail angle using angle of attack function
        optimal_angle = angle_of_attack(relative_wind.calc())
        self.boat.sails[0].setSailRotation(Angle(1, optimal_angle))



# Backward compatibility alias (Controler was a typo, now fixed to Controller)
Controler = Controller
