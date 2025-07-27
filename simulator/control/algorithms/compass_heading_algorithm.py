"""
Compass Heading Algorithm - Maintains a specific compass heading
"""

from ...utils.control_algorithms import ControlAlgorithm
from ...core.Variables import Angle


class CompassHeadingAlgorithm(ControlAlgorithm):
    """Maintains a specific compass heading regardless of wind"""
    
    def __init__(self, boat, controller, target_heading=0):
        super().__init__(boat, controller)
        self.target_heading = target_heading  # Compass heading in degrees
        
    def update(self, dt):
        """Update control to maintain compass heading"""
        # Simple heading control
        target_angle = Angle(1, self.target_heading)
        
        # Steer toward target heading
        self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def set_heading(self, heading):
        """Change target heading"""
        self.target_heading = heading
        
    def get_state_info(self):
        return {
            "algorithm": "Compass Heading",
            "target_heading": self.target_heading,
            "current_heading": self.boat.angle.calc()
        }