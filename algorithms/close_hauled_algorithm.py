"""
Close Hauled Algorithm - Sails as close to the wind as possible
"""

from control_algorithms import ControlAlgorithm
from Variables import Angle
import math


class CloseHauledAlgorithm(ControlAlgorithm):
    """Sails close-hauled (as close to wind as possible)"""
    
    def __init__(self, boat, controller, tack_angle=45):
        super().__init__(boat, controller)
        self.tack_angle = tack_angle  # Degrees off wind
        self.on_starboard = True
        self.tack_timer = 0
        self.tack_interval = 30  # Tack every 30 seconds
        
    def update(self, dt):
        """Update control for close-hauled sailing"""
        # Update tack timer
        self.tack_timer += dt
        
        # Check if time to tack
        if self.tack_timer >= self.tack_interval:
            self.on_starboard = not self.on_starboard
            self.tack_timer = 0
            print(f"Tacking to {'starboard' if self.on_starboard else 'port'}")
        
        # Get wind direction
        wind_angle = self.boat.wind.angle.calc()
        
        # Calculate close-hauled angle
        if self.on_starboard:
            target_angle = Angle(1, wind_angle + self.tack_angle)
        else:
            target_angle = Angle(1, wind_angle - self.tack_angle)
        
        # Steer to maintain close-hauled course
        self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def get_state_info(self):
        return {
            "algorithm": "Close Hauled",
            "tack": "Starboard" if self.on_starboard else "Port",
            "angle_to_wind": self.tack_angle,
            "time_to_tack": self.tack_interval - self.tack_timer
        }