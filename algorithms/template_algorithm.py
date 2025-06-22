"""
Template Algorithm - Copy this file to create your own algorithm

Steps:
1. Copy this file and rename it (e.g., my_algorithm.py)
2. Rename the class from TemplateAlgorithm to your algorithm name
3. Implement your control logic in the update() method
4. Update simulator_config.py to use your algorithm
"""

from control_algorithms import ControlAlgorithm
from Variables import Angle
import math


class TemplateAlgorithm(ControlAlgorithm):
    """Description of your algorithm"""
    
    def __init__(self, boat, controller):
        super().__init__(boat, controller)
        # Initialize any variables your algorithm needs
        self.my_variable = 0
        
    def update(self, dt):
        """
        Main control loop - called every timestep
        
        Available boat data:
        - self.boat.position - Current position vector
        - self.boat.linearVelocity - Current velocity vector
        - self.boat.angle.calc() - Current heading in degrees
        - self.boat.wind.angle.calc() - Wind direction in degrees
        - self.boat.wind.norm - Wind speed
        - self.boat.globalAparentWind() - Apparent wind vector
        
        Control outputs:
        - self.controller.updateRudderAngle(noise, stability, target_angle)
        - self.controller.updateSails()
        
        Navigation utilities available from navigation_utils:
        - normalize_angle(angle) - Convert to [-180, 180]
        - calculate_bearing(from_pos, to_pos) - Get bearing between points
        - calculate_distance(pos1, pos2) - Distance between points
        """
        
        # IMPLEMENT YOUR ALGORITHM HERE
        
        # Example: Sail at a fixed angle to the wind
        wind_angle = self.boat.wind.angle.calc()
        target_angle = Angle(1, wind_angle + 60)  # 60 degrees off wind
        
        # Apply control
        self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def get_state_info(self):
        """Return information about your algorithm's state"""
        return {
            "algorithm": "Template Algorithm",
            "my_variable": self.my_variable
        }