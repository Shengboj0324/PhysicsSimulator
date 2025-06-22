"""
Navigation utilities for the physics simulator
Contains common navigation functions and helpers
"""

import math
from Variables import Angle, Vector


def normalize_angle(angle):
    """
    Normalize angle to [-180, 180] range
    
    Args:
        angle: Angle in degrees
        
    Returns:
        Normalized angle between -180 and 180 degrees
    """
    angle %= 360
    if angle > 180:
        angle = -180 + angle - 180
    return angle


def angle_of_attack(angle):
    """
    Calculate angle of attack for sail/foil
    
    Args:
        angle: Input angle in degrees
        
    Returns:
        Angle of attack
    """
    angle = normalize_angle(angle)
    return (44/90) * angle


def calculate_bearing(from_point, to_point):
    """
    Calculate bearing from one point to another
    
    Args:
        from_point: [x, y] starting coordinates
        to_point: [x, y] target coordinates
        
    Returns:
        Bearing in degrees (0-360)
    """
    dx = to_point[0] - from_point[0]
    dy = to_point[1] - from_point[1]
    bearing = math.atan2(dy, dx) * 180 / math.pi
    return bearing % 360


def calculate_distance(point1, point2):
    """
    Calculate distance between two points
    
    Args:
        point1: [x, y] coordinates
        point2: [x, y] coordinates
        
    Returns:
        Distance in coordinate units
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx**2 + dy**2)


def is_upwind(target_bearing, wind_angle, no_go_angle=45):
    """
    Check if target bearing is in the upwind no-go zone
    
    Args:
        target_bearing: Bearing to target in degrees
        wind_angle: Wind direction in degrees
        no_go_angle: Half-angle of no-go zone (default 45°)
        
    Returns:
        Boolean indicating if bearing is upwind
    """
    relative_angle = abs(normalize_angle(target_bearing - wind_angle))
    return relative_angle < no_go_angle


def is_downwind(target_bearing, wind_angle, no_go_angle=30):
    """
    Check if target bearing is in the downwind no-go zone
    
    Args:
        target_bearing: Bearing to target in degrees
        wind_angle: Wind direction in degrees  
        no_go_angle: Half-angle of downwind no-go zone (default 30°)
        
    Returns:
        Boolean indicating if bearing is downwind
    """
    relative_angle = abs(normalize_angle(target_bearing - wind_angle))
    return abs(180 - relative_angle) < no_go_angle


def calculate_vmg(boat_speed, boat_heading, target_bearing):
    """
    Calculate Velocity Made Good toward target
    
    Args:
        boat_speed: Current boat speed
        boat_heading: Current boat heading in degrees
        target_bearing: Bearing to target in degrees
        
    Returns:
        VMG (positive toward target, negative away)
    """
    angle_diff = normalize_angle(target_bearing - boat_heading)
    return boat_speed * math.cos(math.radians(angle_diff))


def calculate_twa(boat_heading, wind_angle):
    """
    Calculate True Wind Angle (angle between boat heading and wind)
    
    Args:
        boat_heading: Boat's heading in degrees
        wind_angle: Wind direction in degrees
        
    Returns:
        TWA in degrees (0-180, where 0 is head to wind)
    """
    twa = abs(normalize_angle(wind_angle - boat_heading))
    if twa > 180:
        twa = 360 - twa
    return twa


def calculate_awa(boat_velocity, wind_vector):
    """
    Calculate Apparent Wind Angle and speed
    
    Args:
        boat_velocity: Vector of boat's velocity
        wind_vector: Vector of true wind
        
    Returns:
        Tuple of (apparent_wind_angle, apparent_wind_speed)
    """
    apparent_wind = wind_vector - boat_velocity
    awa = apparent_wind.angle.calc()
    aws = apparent_wind.norm
    return awa, aws


def optimal_tack_angles(wind_angle, boat_polars, upwind_angle=45):
    """
    Calculate optimal tacking angles based on wind and boat polars
    
    Args:
        wind_angle: Current wind direction in degrees
        boat_polars: Boat polar data
        upwind_angle: Optimal upwind sailing angle (default 45°)
        
    Returns:
        Tuple of (port_tack_heading, starboard_tack_heading)
    """
    port_tack = (wind_angle + upwind_angle) % 360
    stbd_tack = (wind_angle - upwind_angle) % 360
    return port_tack, stbd_tack


def layline_intersection(current_pos, mark_pos, wind_angle, tack_angle):
    """
    Calculate layline intersection point for upwind mark
    
    Args:
        current_pos: Current boat position [x, y]
        mark_pos: Mark position [x, y]
        wind_angle: Wind direction in degrees
        tack_angle: Angle to sail relative to wind
        
    Returns:
        Intersection point [x, y] or None if no intersection
    """
    # Calculate layline from mark
    layline_angle = (wind_angle + tack_angle) % 360
    
    # Vector from current position to mark
    dx = mark_pos[0] - current_pos[0]
    dy = mark_pos[1] - current_pos[1]
    
    # Project onto layline
    distance_to_mark = math.sqrt(dx**2 + dy**2)
    bearing_to_mark = math.atan2(dy, dx) * 180 / math.pi
    
    # Angle between bearing to mark and layline
    angle_diff = normalize_angle(layline_angle - bearing_to_mark)
    
    if abs(angle_diff) > 90:
        # We're past the layline
        return None
        
    # Calculate projection distance
    projection = distance_to_mark * math.cos(math.radians(angle_diff))
    
    # Calculate intersection point
    inter_x = current_pos[0] + projection * math.cos(math.radians(layline_angle))
    inter_y = current_pos[1] + projection * math.sin(math.radians(layline_angle))
    
    return [inter_x, inter_y]


class NavigationHelper:
    """Helper class with navigation utilities"""
    
    def __init__(self, boat):
        self.boat = boat
        
    def get_relative_wind_angle(self):
        """Get wind angle relative to boat heading"""
        global_wind = self.boat.wind.angle.calc()
        boat_heading = self.boat.angle.calc()
        return normalize_angle(global_wind - boat_heading)
        
    def get_apparent_wind(self):
        """Get apparent wind vector"""
        return self.boat.globalAparentWind()
        
    def distance_to_point(self, target):
        """Calculate distance to target point"""
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        return calculate_distance(current_pos, target)
        
    def bearing_to_point(self, target):
        """Calculate bearing to target point"""
        current_pos = [self.boat.position.xcomp(), self.boat.position.ycomp()]
        return calculate_bearing(current_pos, target)
        
    def vmg_to_point(self, target):
        """Calculate current VMG toward target"""
        bearing = self.bearing_to_point(target)
        boat_speed = self.boat.linearVelocity.norm
        boat_heading = self.boat.linearVelocity.angle.calc()
        return calculate_vmg(boat_speed, boat_heading, bearing)