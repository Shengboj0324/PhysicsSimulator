"""
Simple Rudder Controller

This is the default rudder controller extracted from the original Control.py.
It uses a simple proportional control with rotational velocity damping.
"""

import math
from ..base_controllers import BaseRudderController


class SimpleRudderController(BaseRudderController):
    """
    Simple rudder controller using proportional control with damping.
    
    This controller steers the boat toward a target heading using:
    - Proportional control based on heading error
    - Rotational velocity damping for stability
    - Arctangent saturation to limit control response
    """
    
    def __init__(self, boat, noise_factor=2, stability_factor=1):
        """
        Initialize the simple rudder controller.
        
        Args:
            boat: Reference to the boat object
            noise_factor: Control responsiveness (higher = more responsive)
            stability_factor: Damping factor (higher = more stable)
        """
        super().__init__(boat)
        self.noise_factor = noise_factor
        self.stability_factor = stability_factor
    
    def calculate_rudder_angle(self, target_heading=None, **kwargs):
        """
        Calculate rudder angle to steer toward target heading.
        
        Args:
            target_heading: Target heading in degrees
            **kwargs: Can include 'noise_factor' and 'stability_factor' overrides
            
        Returns:
            float: Rudder angle in degrees (-10 to +10)
        """
        if target_heading is None:
            return 0.0
        
        # Allow parameter overrides
        noise = kwargs.get('noise_factor', self.noise_factor)
        stability = kwargs.get('stability_factor', self.stability_factor)
        
        # Get current heading from boat velocity
        current_heading = self.boat.linearVelocity.angle.calc()
        
        # Calculate heading error
        heading_error = self._normalize_angle(target_heading - current_heading)
        
        # Get rotational velocity for damping
        rot_velocity = self.boat.rotationalVelocity
        
        # Control law: proportional control with velocity damping
        # Uses arctangent for saturation
        control_signal = 2/math.pi * math.atan(heading_error/40 - rot_velocity/stability)
        
        # Scale by noise factor and apply physical limits
        rudder_angle = -10 * control_signal * noise
        
        return rudder_angle
    
    def _normalize_angle(self, angle):
        """Normalize angle to [-180, 180] range."""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle


class WaypointRudderController(SimpleRudderController):
    """
    Rudder controller that steers toward waypoints.
    
    Extends the simple rudder controller to automatically calculate
    target headings based on waypoint positions.
    """
    
    def steer_to_waypoint(self, waypoint, **kwargs):
        """
        Steer the boat toward a specific waypoint.
        
        Args:
            waypoint: [x, y] coordinates of the target waypoint
            **kwargs: Additional parameters passed to calculate_rudder_angle
            
        Returns:
            float: Rudder angle in degrees
        """
        # Calculate bearing to waypoint
        dx = waypoint[0] - self.boat.position.xcomp()
        dy = waypoint[1] - self.boat.position.ycomp()
        target_heading = math.atan2(dy, dx) * 180 / math.pi
        
        # Use base controller to calculate rudder angle
        angle = self.calculate_rudder_angle(target_heading, **kwargs)
        
        # Apply the rudder angle
        self.apply_rudder(angle)
        
        return angle