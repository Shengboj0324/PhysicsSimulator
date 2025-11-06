"""
Variable, Angle, and Vector classes for the Physics Sailing Simulator

This module provides the core data types for representing angles, vectors,
and variables with different coordinate systems and type conversions.

Enhanced with type hints, validation, and error handling.
"""

import math
import copy
from typing import Union, Tuple, Optional

# Import validation and error handling
try:
    from .validators import Validator
    from .exceptions import AngleError, VectorError, ValidationError
    from .constants import (
        ANGLE_TYPE_DATA, ANGLE_TYPE_CALC, ANGLE_TYPE_DISPLAY,
        METERS_PER_DEGREE_LAT, METERS_PER_DEGREE_LON_APPROX,
        DEG_TO_RAD, RAD_TO_DEG, EPSILON
    )
    from .logger import logger
except ImportError:
    # Fallback for backward compatibility
    class Validator:
        @staticmethod
        def validate_angle(value, name="angle", min_val=-float('inf'), max_val=float('inf')):
            return float(value)
        @staticmethod
        def validate_vector_magnitude(magnitude, name="magnitude"):
            return float(magnitude)
        @staticmethod
        def safe_divide(num, denom, default=0.0):
            return num / denom if abs(denom) > 1e-10 else default

    class AngleError(Exception):
        pass
    class VectorError(Exception):
        pass
    class ValidationError(Exception):
        pass

    ANGLE_TYPE_DATA = 0
    ANGLE_TYPE_CALC = 1
    ANGLE_TYPE_DISPLAY = 2
    METERS_PER_DEGREE_LAT = 111111.0
    METERS_PER_DEGREE_LON_APPROX = 111320.0
    DEG_TO_RAD = math.pi / 180.0
    RAD_TO_DEG = 180.0 / math.pi
    EPSILON = 1e-10

    class logger:
        @staticmethod
        def debug(msg, **kwargs):
            pass
        @staticmethod
        def warning(msg, **kwargs):
            pass


class Variable:
    """
    Base variable class supporting multiple type systems.

    Type 0 (DATA): Data variable format
    Type 1 (CALC): Calculation format
    Type 2 (DISPLAY): Display format
    """

    def __init__(self, var_type: int, value: float):
        """
        Initialize variable

        Args:
            var_type: Variable type (0=data, 1=calc, 2=display)
            value: Variable value

        Raises:
            ValidationError: If inputs are invalid
        """
        if var_type not in [0, 1, 2]:
            raise ValidationError(f"Invalid variable type: {var_type}. Must be 0, 1, or 2")

        if not isinstance(value, (int, float)):
            raise ValidationError(f"Value must be numeric, got {type(value)}")

        if math.isnan(value):
            raise ValidationError("Value cannot be NaN")

        if math.isinf(value):
            raise ValidationError("Value cannot be infinite")

        self.type: int = var_type
        self.value: float = float(value)

    def data(self) -> float:
        """Get value in data format"""
        return self.value

    def calc(self) -> float:
        """Get value in calculation format"""
        return self.value

    def display(self) -> float:
        """Get value in display format"""
        return self.value

    def changeType(self, var_type: int) -> None:
        """
        Change variable type and convert value

        Args:
            var_type: New variable type (0=data, 1=calc, 2=display)
        """
        if var_type not in [0, 1, 2]:
            raise ValidationError(f"Invalid variable type: {var_type}")

        if var_type == 0:
            self.value = self.data()
        elif var_type == 1:
            self.value = self.calc()
        elif var_type == 2:
            self.value = self.display()

        self.type = var_type

    def nType(self, var_type: int) -> float:
        """
        Get value in specified type without changing internal type

        Args:
            var_type: Desired type (0=data, 1=calc, 2=display)

        Returns:
            Value in specified type
        """
        if var_type == 0:
            return self.data()
        elif var_type == 1:
            return self.calc()
        else:
            return self.display()

    def __str__(self) -> str:
        """String representation"""
        type_names = {0: "Data", 1: "Calc", 2: "Display"}
        rounded_value = round(self.value * 10000) / 10000
        return f"{type_names.get(self.type, 'Unknown')}: {rounded_value}"

    def __add__(self, other: 'Variable') -> 'Variable':
        """Add two variables (result in type of left operand)"""
        return Variable(self.type, self.value + other.nType(self.type))

    def __sub__(self, other: 'Variable') -> 'Variable':
        """Subtract two variables (result in type of left operand)"""
        return Variable(self.type, self.value - other.nType(self.type))

    def __mul__(self, other: 'Variable') -> 'Variable':
        """Multiply two variables (result in type of left operand)"""
        return Variable(self.type, self.value * other.nType(self.type))

class Angle(Variable):
    """
    Angle class with multiple coordinate system support.

    Type 0 (DATA): Data angles (0-180° range for foil data)
       |0
 (-)90--- 90
       |180

    Type 1 (CALC): Calc angles (Unit circle: 0° = East, 90° = North)
       |90
   180---0
       |270

    Type 2 (DISPLAY): Display angles (0-360° with negatives allowed)
       | 90
     0--- 180
       |270
    """

    def __init__(self, angle_type: int, value: float):
        """
        Initialize angle

        Args:
            angle_type: Angle type (0=data, 1=calc, 2=display)
            value: Angle value in degrees

        Raises:
            AngleError: If inputs are invalid
        """
        # Validate before calling parent constructor
        if angle_type not in [0, 1, 2]:
            raise AngleError(f"Invalid angle type: {angle_type}. Must be 0, 1, or 2")

        if not isinstance(value, (int, float)):
            raise AngleError(f"Angle value must be numeric, got {type(value)}")

        if math.isnan(value):
            raise AngleError("Angle value cannot be NaN")

        if math.isinf(value):
            raise AngleError("Angle value cannot be infinite")

        # Call parent constructor
        super().__init__(angle_type, value)

    def data(self) -> float:
        """Get angle in data format"""
        if self.type == 1:
            return self.calc2data()
        elif self.type == 2:
            return self.display2data()
        return self.value

    def calc(self) -> float:
        """Get angle in calculation format"""
        if self.type == 0:
            return self.data2calc()
        elif self.type == 2:
            return self.display2calc()
        return self.value

    def display(self) -> float:
        """Get angle in display format"""
        if self.type == 0:
            return self.data2display()
        elif self.type == 1:
            return self.calc2display()
        return self.value

    def display2data(self) -> float:
        """Convert display angle to data angle"""
        if self.value <= 180:
            return self.value - 90
        else:  # Avoid negatives
            return 180 - (self.value - 90) % 180

    def display2calc(self) -> float:
        """Convert display angle to calc angle"""
        return 180 - self.value

    def data2display(self) -> float:
        """Convert data angle to display angle"""
        return self.value + 90

    def data2calc(self) -> float:
        """Convert data angle to calc angle (may lose information)"""
        return 90 - self.value

    def calc2display(self) -> float:
        """Convert calc angle to display angle"""
        return -self.value + 180

    def calc2data(self) -> float:
        """Convert calc angle to data angle"""
        normalized = self.norm(self)
        if normalized.value <= 180:
            return normalized.value
        else:
            return -(360 - normalized.value)

    @staticmethod
    def norm(angle: 'Angle') -> 'Angle':
        """
        Normalize angle to appropriate range based on type

        Args:
            angle: Angle to normalize

        Returns:
            Normalized angle
        """
        if angle.type in [1, 2]:  # calc and display
            angle.value %= 360
        return angle

    def __str__(self) -> str:
        """String representation with color coding"""
        return "\033[96mAngle\033[0m: " + super().__str__()

    def __add__(self, other: Union['Angle', float, int]) -> 'Angle':
        """Add angles (result in type of left operand)"""
        if isinstance(other, (int, float)):
            return Angle(self.type, self.norm(self).value + other)
        return Angle(self.type, self.norm(self).value + self.norm(other).nType(self.type))

    def __sub__(self, other: Union['Angle', float, int]) -> 'Angle':
        """Subtract angles (result in type of left operand)"""
        if isinstance(other, (int, float)):
            return Angle(self.type, self.norm(self).value - other)
        return Angle(self.type, self.norm(self).value - self.norm(other).nType(self.type))

    def __mul__(self, other: Union['Angle', float, int]) -> 'Angle':
        """Multiply angle (result in type of left operand)"""
        if isinstance(other, (int, float)):
            return Angle(self.type, self.norm(self).value * other)
        else:
            return Angle(self.type, self.norm(self).value * self.norm(other).nType(self.type))

def meter2degreeY(displacement: float) -> float:
    """
    Convert meters to degrees of latitude

    Args:
        displacement: Displacement in meters

    Returns:
        Displacement in degrees of latitude

    Raises:
        ValidationError: If displacement is invalid
    """
    if math.isnan(displacement) or math.isinf(displacement):
        raise ValidationError(f"Invalid displacement: {displacement}")

    return Validator.safe_divide(displacement, METERS_PER_DEGREE_LAT, 0.0)


def meter2degreeX(displacement: float, latitude: float) -> float:
    """
    Convert meters to degrees of longitude at given latitude

    Args:
        displacement: Displacement in meters
        latitude: Reference latitude in degrees

    Returns:
        Displacement in degrees of longitude

    Raises:
        ValidationError: If inputs are invalid
    """
    if math.isnan(displacement) or math.isinf(displacement):
        raise ValidationError(f"Invalid displacement: {displacement}")

    if math.isnan(latitude) or math.isinf(latitude):
        raise ValidationError(f"Invalid latitude: {latitude}")

    # Use simplified conversion (not accounting for latitude variation)
    # For small areas, this is acceptable
    return Validator.safe_divide(displacement, METERS_PER_DEGREE_LAT, 0.0)


def degree2meter(displacement: float) -> float:
    """
    Convert degrees to meters (approximate)

    Note: This is an approximation that works for small areas.
    For precise conversions, use proper geodetic calculations.

    Args:
        displacement: Displacement in degrees

    Returns:
        Displacement in meters

    Raises:
        ValidationError: If displacement is invalid
    """
    if math.isnan(displacement) or math.isinf(displacement):
        raise ValidationError(f"Invalid displacement: {displacement}")

    return displacement * METERS_PER_DEGREE_LAT

class Vector:
    """
    2D Vector class with angle and magnitude representation.

    Supports vector operations and coordinate conversions.
    """

    def __init__(self, angle: Angle, magnitude: float):
        """
        Initialize vector

        Args:
            angle: Vector angle (Angle object)
            magnitude: Vector magnitude (can be negative)

        Raises:
            VectorError: If inputs are invalid
        """
        if not isinstance(angle, Angle):
            raise VectorError(f"Angle must be an Angle object, got {type(angle)}")

        if not isinstance(magnitude, (int, float)):
            raise VectorError(f"Magnitude must be numeric, got {type(magnitude)}")

        if math.isnan(magnitude):
            raise VectorError("Magnitude cannot be NaN")

        if math.isinf(magnitude):
            raise VectorError("Magnitude cannot be infinite")

        self.angle: Angle = angle
        self.norm: float = float(magnitude)

    def speed(self) -> float:
        """
        Get vector magnitude (for displacement/speed vectors)

        Returns:
            Vector magnitude
        """
        return self.norm

    def xcomp(self) -> float:
        """
        Get x component of vector in calc format

        Returns:
            X component
        """
        return math.cos(self.angle.calc() * DEG_TO_RAD) * self.speed()

    def ycomp(self) -> float:
        """
        Get y component of vector in calc format

        Returns:
            Y component
        """
        return math.sin(self.angle.calc() * DEG_TO_RAD) * self.speed()

    def meter2degree(self, lat: float) -> 'Vector':
        """
        Convert vector from meters to degrees

        Args:
            lat: Reference latitude in degrees

        Returns:
            Vector in degree coordinates
        """
        dLat = meter2degreeY(self.ycomp())
        dLon = meter2degreeX(self.xcomp(), lat)

        # Calculate angle and magnitude
        magnitude = math.sqrt(dLon**2 + dLat**2)

        # Avoid division by zero in atan2
        if abs(dLon) < EPSILON and abs(dLat) < EPSILON:
            angle_deg = 0.0
        else:
            angle_deg = math.atan2(dLat, dLon) * RAD_TO_DEG

        return Vector(Angle(1, round(angle_deg * 10000) / 10000), magnitude)

    def degree2meter(self, lat: float) -> 'Vector':
        """
        Convert vector from degrees to meters

        Args:
            lat: Reference latitude in degrees

        Returns:
            Vector in meter coordinates
        """
        dLat = self.ycomp() * METERS_PER_DEGREE_LAT
        dLon = self.xcomp() * METERS_PER_DEGREE_LAT

        # Calculate angle and magnitude
        magnitude = math.sqrt(dLon**2 + dLat**2)

        # Avoid division by zero in atan2
        if abs(dLon) < EPSILON and abs(dLat) < EPSILON:
            angle_deg = 0.0
        else:
            angle_deg = math.atan2(dLat, dLon) * RAD_TO_DEG

        return Vector(Angle(1, round(angle_deg * 10000) / 10000), magnitude)

    def __add__(self, other: 'Vector') -> 'Vector':
        """
        Add two vectors (returns result in calc format)

        Args:
            other: Vector to add

        Returns:
            Sum vector
        """
        # Component-wise addition
        dx = self.xcomp() + other.xcomp()
        dy = self.ycomp() + other.ycomp()

        # Calculate magnitude
        magnitude = math.sqrt(dx**2 + dy**2)

        # Calculate angle (avoid division by zero)
        if abs(dx) < EPSILON and abs(dy) < EPSILON:
            angle_deg = 0.0
        else:
            angle_deg = math.atan2(dy, dx) * RAD_TO_DEG

        return Vector(Angle(1, angle_deg), magnitude)

    def __mul__(self, other: Union['Vector', float, int]) -> Union['Vector', float]:
        """
        Multiply vector by scalar or compute dot product with another vector

        Args:
            other: Scalar or Vector

        Returns:
            Scaled vector (if scalar) or dot product (if Vector)
        """
        if isinstance(other, Vector):
            # Dot product
            angle_diff = (other.angle.calc() - self.angle.calc()) * DEG_TO_RAD
            return self.norm * other.norm * math.cos(angle_diff)
        else:
            # Scalar multiplication
            return Vector(self.angle, self.norm * other)

    def __sub__(self, other: 'Vector') -> 'Vector':
        """
        Subtract two vectors

        Args:
            other: Vector to subtract

        Returns:
            Difference vector
        """
        negated = copy.deepcopy(other)
        negated.norm = -negated.norm
        return self + negated

    def __str__(self) -> str:
        """String representation with color coding"""
        rounded_norm = round(self.norm * 10000) / 10000
        return f"\033[93mVector\033[0m, norm: {rounded_norm}, {Angle.norm(self.angle)}"