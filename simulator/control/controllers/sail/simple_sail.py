"""
Simple Sail Controller

This is the default sail controller extracted from the original Control.py.
It uses the angle of attack function to determine optimal sail trim.
"""

from ..base_controllers import BaseSailController


def angle_of_attack(apparent_wind_angle):
    """
    Calculate optimal angle of attack for the sail.
    
    This function was originally in navigation_utils.py.
    
    Args:
        apparent_wind_angle: Apparent wind angle in degrees
        
    Returns:
        float: Optimal sail angle in degrees
    """
    awa = abs(apparent_wind_angle)
    
    # Dead run - sail perpendicular to wind
    if awa > 170:
        return 90
    
    # Broad reach to dead run transition
    elif awa > 135:
        # Linear interpolation between 45° and 90°
        return 45 + (awa - 135) * (90 - 45) / (170 - 135)
    
    # Beam reach to broad reach
    elif awa > 90:
        # Sail at approximately 45° off centerline
        return 45
    
    # Close hauled to beam reach
    else:
        # Sail closer to centerline as we point higher
        # Approximately half the apparent wind angle
        return awa * 0.5


class SimpleSailController(BaseSailController):
    """
    Simple sail controller using angle of attack optimization.
    
    This controller trims the sail based on the apparent wind angle
    to maintain an efficient angle of attack.
    """
    
    def calculate_sail_angle(self, apparent_wind_angle, **kwargs):
        """
        Calculate optimal sail angle based on apparent wind.
        
        Args:
            apparent_wind_angle: Apparent wind angle relative to boat in degrees
            **kwargs: Additional parameters (not used in simple controller)
            
        Returns:
            float: Optimal sail angle in degrees
        """
        return angle_of_attack(apparent_wind_angle)
    
    def update_sail_trim(self):
        """
        Update sail trim based on current wind conditions.
        
        This method calculates apparent wind and applies the optimal sail angle.
        """
        from ....core.Variables import Angle
        
        # Get apparent wind angle
        apparent_wind = self.boat.globalAparentWind().angle
        apparent_wind += Angle(1, 180)  # Convert to angle wind is coming FROM
        
        # Get relative wind angle to boat
        relative_wind = apparent_wind - self.boat.angle
        relative_wind_angle = relative_wind.calc()
        
        # Calculate and apply optimal sail angle
        optimal_angle = self.calculate_sail_angle(relative_wind_angle)
        self.apply_sail_angle(optimal_angle)
        
        return optimal_angle


class PolarBasedSailController(BaseSailController):
    """
    Advanced sail controller that uses polar diagrams.
    
    This controller can optimize sail trim based on boat performance
    data from polar diagrams.
    """
    
    def __init__(self, boat, polars):
        """
        Initialize polar-based sail controller.
        
        Args:
            boat: Reference to the boat object
            polars: Polar diagram data
        """
        super().__init__(boat)
        self.polars = polars
    
    def calculate_sail_angle(self, apparent_wind_angle, **kwargs):
        """
        Calculate sail angle using polar optimization.
        
        This is a placeholder for more advanced sail trim optimization
        based on polar performance data.
        
        Args:
            apparent_wind_angle: Apparent wind angle relative to boat in degrees
            wind_speed: Wind speed for polar lookup (optional)
            
        Returns:
            float: Optimal sail angle in degrees
        """
        # For now, fall back to simple angle of attack
        # TODO: Implement polar-based optimization
        return angle_of_attack(apparent_wind_angle)