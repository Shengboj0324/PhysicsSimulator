"""
Example: Zigzag Algorithm - Shows how easy it is to create a new algorithm
"""

from ...utils.control_algorithms import ControlAlgorithm
from ...core.Variables import Angle
import math


class ZigzagAlgorithm(ControlAlgorithm):
    """Sails in a zigzag pattern by alternating between port and starboard reaches"""
    
    def __init__(self, boat, controller):
        super().__init__(boat, controller)
        self.zigzag_timer = 0
        self.zigzag_period = 10  # seconds
        self.on_starboard = True
        
    def update(self, dt):
        # Update timer
        self.zigzag_timer += dt
        
        # Switch tack every period
        if self.zigzag_timer >= self.zigzag_period:
            self.on_starboard = not self.on_starboard
            self.zigzag_timer = 0
            print(f"Zigzag: Turning to {'starboard' if self.on_starboard else 'port'}")
        
        # Get wind direction
        wind_angle = self.boat.wind.angle.calc()
        
        # Zigzag at 60 degrees off wind
        if self.on_starboard:
            target_angle = Angle(1, wind_angle + 60)
        else:
            target_angle = Angle(1, wind_angle - 60)
        
        # Apply control
        self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def get_state_info(self):
        return {
            "algorithm": "Zigzag Pattern",
            "direction": "Starboard" if self.on_starboard else "Port",
            "time_to_turn": self.zigzag_period - self.zigzag_timer
        }