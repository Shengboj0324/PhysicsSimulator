import math
import numpy as np
from ..core.Variables import *
from ..utils.control_algorithms import (
    ControlAlgorithm,
    WaypointFollowingAlgorithm,
    StationKeepingAlgorithm,
    DirectControlAlgorithm,
    VMGOptimizationAlgorithm
)
from ..utils.navigation_utils import normalize_angle, angle_of_attack

# Navigation utility functions moved to navigation_utils.py
printA = normalize_angle  # Alias for backward compatibility
aoa = angle_of_attack    # Alias for backward compatibility

class Controler():
    """Main controller that manages different control algorithms"""
    
    def __init__(self, Boat, polars="data/test.pol"):
        self.boat = Boat
        self.polars = self.readPolar(polars)
        self.active_course = []
        self.current_algorithm = None
        self.display = None
        

    def plan(self, plantype, waypoints):
        """Initialize control algorithm based on plan type"""
        if plantype == "e" or plantype == "p":  # endurance or precision
            self.current_algorithm = WaypointFollowingAlgorithm(self.boat, self, waypoints, plantype)
            self.current_algorithm.calculate_next_legs()
            return self.active_course
            
        elif plantype == "s":  # station keeping
            self.current_algorithm = StationKeepingAlgorithm(self.boat, self, waypoints)
            return self.active_course
            
        else:
            raise ValueError(f"Unknown plan type: {plantype}")
        
    def set_algorithm(self, algorithm):
        """Set a custom control algorithm"""
        if not isinstance(algorithm, ControlAlgorithm):
            raise TypeError("Algorithm must be a ControlAlgorithm instance")
        self.current_algorithm = algorithm

    def leg(self, start, stop):
        """Calculate path between two points, handling no-go zones"""
        # Calculate direct course
        dx = stop[0] - start[0]
        dy = stop[1] - start[1]
        course_angle = Angle(1, math.atan2(dy, dx) * 180/math.pi)
        distance = math.sqrt(dx**2 + dy**2)
        
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
        upwind_nogo = self.polars[-1][0]
        downwind_nogo = 180 - self.polars[-1][1]
        
        # Check if we need to tack (upwind)
        if angle_to_wind < upwind_nogo:
            return self._calculate_tacking_path(start, stop, relative_wind, 
                                              boat_heading, upwind_nogo, 
                                              course_angle, distance)
        
        # Check if we need to jibe (downwind)
        elif (180 - angle_to_wind) < downwind_nogo:
            return self._calculate_jibing_path(start, stop, relative_wind,
                                             boat_heading, downwind_nogo,
                                             course_angle, distance)
        
        # Direct course is possible
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