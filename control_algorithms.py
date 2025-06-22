from abc import ABC, abstractmethod
import math
from Variables import *
from station_keeping import StationKeepingController


class ControlAlgorithm(ABC):
    """Base class for all control algorithms"""
    
    def __init__(self, boat, controller):
        self.boat = boat
        self.controller = controller
        
    @abstractmethod
    def update(self, dt):
        """Update control logic - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def get_state_info(self):
        """Get current state information for debugging"""
        pass


class WaypointFollowingAlgorithm(ControlAlgorithm):
    """Standard waypoint following control algorithm"""
    
    def __init__(self, boat, controller, waypoints, course_type):
        super().__init__(boat, controller)
        self.waypoints = waypoints
        self.course_type = course_type
        self.current_target_idx = 0
        self.active_course = []
        self.last_recalc_time = 0
        self.recalc_interval = 1.0
        
    def update(self, dt):
        """Update waypoint following logic"""
        if self.target_reached():
            if self.course_type == "e" and self.current_target_idx >= len(self.waypoints) - 1:
                self.current_target_idx = 0
                print("Completed lap, continuing endurance course")
            else:
                self.current_target_idx += 1
            
            self.calculate_next_legs()
            self.last_recalc_time = 0
        
        self.last_recalc_time += dt
        if self.last_recalc_time >= self.recalc_interval:
            self.recalculate_current_leg()
            self.last_recalc_time = 0
        
        self.controller.updateRudder(2, 1)
        self.controller.updateSails()
        
    def target_reached(self):
        """Check if current target waypoint has been reached"""
        if self.current_target_idx >= len(self.waypoints) and self.course_type != "e":
            return False
            
        current_target = self.waypoints[self.current_target_idx % len(self.waypoints)]
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        
        dx = current_target[0] - current_pos[0]
        dy = current_target[1] - current_pos[1]
        dist = degree2meter(math.sqrt(dx**2 + dy**2))
        
        if dist < 5:
            print(f"Reached target {self.current_target_idx % len(self.waypoints)}")
            return True
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
            
    def recalculate_current_leg(self):
        """Recalculate path to current target"""
        if self.current_target_idx >= len(self.waypoints):
            return
            
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        target_waypoint = self.waypoints[self.current_target_idx]
        
        print(f"Recalculating path from current pos to target: {target_waypoint}")
        
        new_leg = self.controller.leg(current_pos, target_waypoint)
        
        self.active_course = [current_pos]
        if isinstance(new_leg, list):
            self.active_course.extend(new_leg)
        
        self.controller.active_course = self.active_course
        
        if hasattr(self.controller, 'display'):
            self.controller.display.clear_paths()
            self.controller.display.boat.plotCourse(self.active_course, 'green')
            
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
    """Velocity Made Good optimization algorithm"""
    
    def __init__(self, boat, controller, target_point):
        super().__init__(boat, controller)
        self.target_point = target_point
        self.optimization_interval = 2.0
        self.last_optimization_time = 0
        self.current_heading = None
        
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
        
    def optimize_heading(self):
        """Find optimal heading for best VMG to target"""
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        
        dx = self.target_point[0] - current_pos[0]
        dy = self.target_point[1] - current_pos[1]
        target_bearing = math.atan2(dy, dx) * 180 / math.pi
        
        wind_angle = self.boat.wind.angle.calc()
        relative_wind = printA(wind_angle - self.boat.angle.calc())
        
        best_vmg = -float('inf')
        best_heading = target_bearing
        
        for heading_offset in range(-90, 91, 5):
            test_heading = target_bearing + heading_offset
            relative_wind_at_heading = printA(wind_angle - test_heading)
            
            boat_speed = self.controller.VB(Angle(1, abs(relative_wind_at_heading)), self.boat.wind.norm)
            if boat_speed > 0:
                vmg = boat_speed * math.cos(math.radians(heading_offset))
                if vmg > best_vmg:
                    best_vmg = vmg
                    best_heading = test_heading
                    
        self.current_heading = best_heading
        print(f"Optimized heading: {best_heading:.1f}° for VMG: {best_vmg:.2f}")
        
    def get_state_info(self):
        """Get current algorithm state"""
        return {
            "algorithm": "VMG Optimization",
            "target": self.target_point,
            "current_heading": self.current_heading
        }


def printA(x):
    """Normalize angle to [-180, 180]"""
    x %= 360
    if x > 180:
        x = -180 + x - 180
    return x