"""
Beam Reach Algorithm - Maintains a beam reach (90° to wind)
"""

from control_algorithms import ControlAlgorithm
from Variables import Angle


class BeamReachAlgorithm(ControlAlgorithm):
    """Maintains a beam reach (90 degrees to the wind) for maximum speed"""
    
    def __init__(self, boat, controller, starboard=True):
        super().__init__(boat, controller)
        self.starboard = starboard  # True for starboard tack, False for port
        
    def update(self, dt):
        """Update control to maintain beam reach"""
        # Get wind direction
        wind_angle = self.boat.wind.angle.calc()
        
        # Calculate beam reach angle (90 degrees off wind)
        if self.starboard:
            target_angle = Angle(1, wind_angle + 90)
        else:
            target_angle = Angle(1, wind_angle - 90)
        
        # Steer to maintain beam reach
        self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def get_state_info(self):
        return {
            "algorithm": "Beam Reach",
            "tack": "Starboard" if self.starboard else "Port",
            "wind_angle": self.boat.wind.angle.calc()
        }