"""
Simple Pathfinding Controller

This is the default pathfinding controller extracted from the original Control.py.
It handles basic navigation including tacking and jibing around no-go zones.
"""

import math
from ..base_controllers import BasePathfindingController


class SimplePathfindingController(BasePathfindingController):
    """
    Simple pathfinding controller with tacking and jibing.
    
    This controller calculates paths between waypoints, automatically
    adding intermediate points when direct paths cross no-go zones.
    """
    
    def __init__(self, boat, controller):
        """
        Initialize the pathfinding controller.
        
        Args:
            boat: Reference to the boat object
            controller: Reference to the main controller (for polars access)
        """
        super().__init__(boat, controller)
        self.arrival_radius = 5.0  # meters
        self.no_go_angle = 45  # degrees from wind
        self.downwind_no_go = 30  # degrees from dead downwind
    
    def calculate_path(self, start_point, end_point, wind_direction, **kwargs):
        """
        Calculate optimal path between two points.
        
        Args:
            start_point: [x, y] starting coordinates
            end_point: [x, y] destination coordinates  
            wind_direction: Current wind direction in degrees
            **kwargs: Can include 'ref_lat' for coordinate conversion
            
        Returns:
            list: List of [x, y] waypoints defining the path
        """
        ref_lat = kwargs.get('ref_lat', self.boat.refLat)
        
        # Calculate bearing to destination
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        bearing = math.atan2(dy, dx) * 180 / math.pi
        
        # Check if path crosses upwind no-go zone
        relative_bearing = self._normalize_angle(bearing - wind_direction)
        
        if abs(relative_bearing) < self.no_go_angle:
            # Need to tack
            return self._calculate_tacking_path(
                start_point, end_point, wind_direction, ref_lat
            )
        elif abs(relative_bearing) > (180 - self.downwind_no_go):
            # Need to jibe
            return self._calculate_jibing_path(
                start_point, end_point, wind_direction, ref_lat
            )
        else:
            # Direct path is fine
            return [end_point]
    
    def _calculate_tacking_path(self, start, end, wind_dir, ref_lat):
        """Calculate tacking path when heading upwind."""
        # Calculate port and starboard tack angles
        port_tack = wind_dir - self.no_go_angle - 5  # 5° margin
        stbd_tack = wind_dir + self.no_go_angle + 5
        
        # Calculate perpendicular distance to wind line
        wind_line_angle = wind_dir * math.pi / 180
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        # Cross track distance
        cross_track = dx * math.sin(wind_line_angle) - dy * math.cos(wind_line_angle)
        
        # Choose initial tack based on cross track position
        if cross_track > 0:
            first_tack = port_tack
            second_tack = stbd_tack
        else:
            first_tack = stbd_tack
            second_tack = port_tack
        
        # Calculate tacking point
        # Go 70% of the way on first tack
        tack_distance = abs(cross_track) * 0.7 / math.sin(self.no_go_angle * math.pi / 180)
        
        # Convert meters to degrees (approximate)
        tack_x = start[0] + (tack_distance * math.cos(first_tack * math.pi / 180)) / 111320
        tack_y = start[1] + (tack_distance * math.sin(first_tack * math.pi / 180)) / 111320
        
        return [[tack_x, tack_y], end]
    
    def _calculate_jibing_path(self, start, end, wind_dir, ref_lat):
        """Calculate jibing path when heading downwind."""
        # Calculate port and starboard jibe angles
        port_jibe = wind_dir + 180 - self.downwind_no_go - 5
        stbd_jibe = wind_dir + 180 + self.downwind_no_go + 5
        
        # Normalize angles
        port_jibe = self._normalize_angle(port_jibe)
        stbd_jibe = self._normalize_angle(stbd_jibe)
        
        # Calculate which side to jibe on
        bearing = math.atan2(end[1] - start[1], end[0] - start[0]) * 180 / math.pi
        relative_bearing = self._normalize_angle(bearing - wind_dir)
        
        if relative_bearing > 0:
            first_jibe = port_jibe
        else:
            first_jibe = stbd_jibe
        
        # Calculate jibing point (halfway to destination)
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Offset perpendicular to wind
        offset_distance = 20  # meters
        offset_angle = first_jibe * math.pi / 180
        
        # Convert meters to degrees (approximate)
        jibe_x = mid_x + (offset_distance * math.cos(offset_angle)) / 111320
        jibe_y = mid_y + (offset_distance * math.sin(offset_angle)) / 111320
        
        return [[jibe_x, jibe_y], end]
    
    def check_waypoint_arrival(self, position, target_waypoint, **kwargs):
        """
        Check if the boat has arrived at a waypoint.
        
        Args:
            position: Current boat position [x, y] or Vector
            target_waypoint: Target waypoint [x, y]
            **kwargs: Can include 'arrival_radius' override
            
        Returns:
            bool: True if waypoint has been reached
        """
        arrival_radius = kwargs.get('arrival_radius', self.arrival_radius)
        ref_lat = kwargs.get('ref_lat', self.boat.refLat)
        
        # Handle Vector position objects
        if hasattr(position, 'xcomp'):
            pos_x = position.xcomp()
            pos_y = position.ycomp()
        else:
            pos_x = position[0]
            pos_y = position[1]
        
        # Calculate distance to waypoint
        dx_deg = target_waypoint[0] - pos_x
        dy_deg = target_waypoint[1] - pos_y
        
        # Convert to meters (approximate)
        dx_m = dx_deg * 111320  # meters per degree longitude
        dy_m = dy_deg * 111320  # meters per degree latitude
        
        distance = math.sqrt(dx_m**2 + dy_m**2)
        
        return distance < arrival_radius
    
    def _normalize_angle(self, angle):
        """Normalize angle to [-180, 180] range."""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle