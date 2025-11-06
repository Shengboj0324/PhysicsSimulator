"""
Foil aerodynamic and hydrodynamic calculations module

This module handles lift and drag calculations for sails, hulls, and rudders
using NACA airfoil data and sail coefficient data.

Enhanced with type hints, validation, and error handling.
"""

import math
from typing import List, Tuple, Optional
from pathlib import Path
from .Variables import Angle, Vector

# Import validation and error handling
try:
    from .validators import Validator
    from .exceptions import FoilDataError, ValidationError, PhysicsError
    from .constants import EPSILON, DEG_TO_RAD, RAD_TO_DEG
    from .logger import logger
except ImportError:
    # Fallback for backward compatibility
    class Validator:
        @staticmethod
        def validate_positive(value, name="value", allow_zero=False):
            return float(value)
        @staticmethod
        def validate_file_exists(filepath, name="file"):
            from pathlib import Path
            return Path(filepath)
        @staticmethod
        def safe_divide(num, denom, default=0.0):
            return num / denom if abs(denom) > 1e-10 else default

    class FoilDataError(Exception):
        pass
    class ValidationError(Exception):
        pass
    class PhysicsError(Exception):
        pass

    EPSILON = 1e-10
    DEG_TO_RAD = math.pi / 180.0
    RAD_TO_DEG = 180.0 / math.pi

    class logger:
        @staticmethod
        def debug(msg, **kwargs):
            pass
        @staticmethod
        def warning(msg, **kwargs):
            pass
        @staticmethod
        def error(msg, **kwargs):
            pass


def printA(x: float) -> float:
    """
    Normalize angle to [-180, 180] range

    Args:
        x: Angle in degrees

    Returns:
        Normalized angle
    """
    x %= 360
    if x > 180:
        x = -180 + x - 180
    return x


class foil:
    """
    Foil class for aerodynamic/hydrodynamic calculations.

    Handles sails, hulls, and rudders with lift and drag coefficients
    from data files.
    """

    def __init__(self,
                 datasheet: str,
                 material: float,
                 WA: float,
                 rotInertia: float = -1,
                 size: float = 1.8,
                 position: Vector = None,
                 winches: List['Winch'] = None):
        """
        Initialize foil

        Args:
            datasheet: Path to coefficient data file (CSV)
            material: Density of fluid (kg/m³) - 997.77 for water, 1.204 for air
            WA: Wetted area (m²)
            rotInertia: Rotational inertia (kg⋅m²)
            size: Length of foil (m)
            position: Position vector relative to boat
            winches: List of winch objects (for sails)

        Raises:
            ValidationError: If inputs are invalid
            FoilDataError: If data file cannot be loaded
        """
        # Validate inputs
        try:
            material = Validator.validate_positive(material, "material density")
            WA = Validator.validate_positive(WA, "wetted area")
            size = Validator.validate_positive(size, "foil size")

            if rotInertia > 0:
                rotInertia = Validator.validate_positive(rotInertia, "rotational inertia")
        except Exception as e:
            raise ValidationError(f"Invalid foil parameters: {e}")

        # Validate datasheet file exists
        try:
            datasheet_path = Validator.validate_file_exists(datasheet, "datasheet")
        except Exception as e:
            raise FoilDataError(f"Datasheet file not found: {datasheet}")

        # Initialize properties
        self.datasheet: str = datasheet
        self.polygon: List[List[float]] = []
        self.size: float = size
        self.mat: float = material
        self.area: float = WA
        self.angle: Angle = Angle(1, 0)
        self.position: Vector = position if position is not None else Vector(Angle(1, 0), 0)
        self.I: float = rotInertia
        self.winches: List['Winch'] = winches if winches is not None else []
        self.rotationalVelocity: float = 0.0

        # Load lift and drag coefficients
        try:
            if "naca" in datasheet.lower():
                self.liftC = self.read(self.datasheet, "Cl")
                self.dragC = self.read(self.datasheet, "Cd")
                self.polygon = self.readPoly(datasheet)
                logger.debug(f"Loaded NACA foil data from {datasheet}")
            elif "mainsailcoeffs" in datasheet.lower():
                self.liftC = self.read(self.datasheet, "clnc-CLlow")
                self.dragC = self.read(self.datasheet, "cdnc-CDlow")
                logger.debug(f"Loaded main sail coefficients from {datasheet}")
            else:
                self.liftC = self.read(self.datasheet, "CL")
                self.dragC = self.read(self.datasheet, "CD")
                if "sail" not in datasheet.lower():
                    self.polygon = self.readPoly(datasheet)
                logger.debug(f"Loaded foil data from {datasheet}")
        except Exception as e:
            raise FoilDataError(f"Failed to load foil data from {datasheet}: {e}")
        
    def readPoly(self, datasheet: str) -> List[List[float]]:
        """
        Read polygon data from .dat file

        Args:
            datasheet: Path to data file

        Returns:
            List of [x, y] coordinate pairs

        Raises:
            FoilDataError: If file cannot be read
        """
        try:
            datasheet = datasheet.replace("cvs", "dat").replace("csv", "dat")

            with open(datasheet, "r") as sheet:
                poly = []
                for line in sheet:
                    if line.strip() and line[0].isnumeric():
                        # Handle both comma-separated and space-separated values
                        if ',' in line:
                            coords = [float(i) for i in line.split(',')]
                        else:
                            coords = [float(i) for i in line.split()]

                        if len(coords) >= 2:
                            coords[0] = -coords[0] + 0.5
                            poly.append(coords)

            logger.debug(f"Loaded {len(poly)} polygon points from {datasheet}")
            return poly

        except FileNotFoundError:
            raise FoilDataError(f"Polygon data file not found: {datasheet}")
        except Exception as e:
            raise FoilDataError(f"Error reading polygon data: {e}")

    def moment(self, force: Vector) -> float:
        """
        Calculate moment (torque) from force

        Args:
            force: Force vector (apparent force)

        Returns:
            Moment in N⋅m
        """
        try:
            angle_rad = force.angle.calc() * DEG_TO_RAD
            moment = -math.sin(angle_rad) * force.norm * self.position.norm

            # Validate result
            if math.isnan(moment) or math.isinf(moment):
                logger.warning(f"Invalid moment calculated: {moment}")
                return 0.0

            return moment

        except Exception as e:
            logger.error(f"Error calculating moment: {e}")
            return 0.0

    def drag(self, aparentV: Vector) -> float:
        """
        Calculate drag force magnitude

        Args:
            aparentV: Apparent velocity vector

        Returns:
            Drag force in Newtons
        """
        try:
            # Flip wind from direction pointing to direction of arrival
            angle_norm = Angle.norm(aparentV.angle + Angle(1, 180))
            cd = self.cd(angle_norm)
            speed = aparentV.speed()

            # Drag formula: 0.5 * Cd * ρ * v² * A
            drag = 0.5 * cd * self.mat * speed * speed * self.area

            # Validate result
            if math.isnan(drag) or math.isinf(drag):
                logger.warning(f"Invalid drag calculated: {drag}")
                return 0.0

            return drag

        except Exception as e:
            logger.error(f"Error calculating drag: {e}")
            return 0.0

    def lift(self, aparentV: Vector) -> float:
        """
        Calculate lift force magnitude

        Args:
            aparentV: Apparent velocity vector

        Returns:
            Lift force in Newtons
        """
        try:
            # Flip wind from direction pointing to direction of arrival
            angle_norm = Angle.norm(aparentV.angle + Angle(1, 180))
            cl = self.cl(angle_norm)
            speed = aparentV.speed()

            # Lift formula: 0.5 * Cl * ρ * v² * A
            lift = 0.5 * cl * self.mat * speed * speed * self.area

            # Validate result
            if math.isnan(lift) or math.isinf(lift):
                logger.warning(f"Invalid lift calculated: {lift}")
                return 0.0

            return lift

        except Exception as e:
            logger.error(f"Error calculating lift: {e}")
            return 0.0


    def liftForce(self, aparentV: Vector) -> Vector:
        """
        Calculate lift force vector

        CONVENTION: Apparent wind should always point in the direction it's going
        (for a hull, that's flow direction)

        Args:
            aparentV: Apparent velocity vector

        Returns:
            Lift force vector (perpendicular to apparent velocity)
        """
        try:
            lift = self.lift(aparentV)

            # Determine lift direction based on port/starboard
            angle_norm = Angle.norm(aparentV.angle).calc()

            if angle_norm >= 180:  # Port side
                if lift < 0:
                    # Negative lift - flip direction, keep magnitude positive
                    return Vector(aparentV.angle + Angle(1, 270), -lift)  # 180+90
                else:
                    return Vector(aparentV.angle + Angle(1, 90), lift)
            else:  # Starboard side
                if lift < 0:
                    # Negative lift - flip direction, keep magnitude positive
                    return Vector(aparentV.angle + Angle(1, 90), -lift)  # 180-90
                else:
                    return Vector(aparentV.angle - Angle(1, 90), lift)

        except Exception as e:
            logger.error(f"Error calculating lift force: {e}")
            return Vector(Angle(1, 0), 0.0)

    def dragForce(self, aparentV: Vector) -> Vector:
        """
        Calculate drag force vector

        Args:
            aparentV: Apparent velocity vector

        Returns:
            Drag force vector (parallel to apparent velocity)
        """
        try:
            drag = self.drag(aparentV)

            # Drag is always opposite to velocity direction
            if drag < 0:
                # Negative drag - flip direction
                return Vector(aparentV.angle + Angle(1, 180), -drag)
            else:
                return Vector(aparentV.angle, drag)

        except Exception as e:
            logger.error(f"Error calculating drag force: {e}")
            return Vector(Angle(1, 0), 0.0)

    def setSailRotation(self, angle: Angle) -> None:
        """
        Set sail rotation angle and update winch lengths

        Args:
            angle: Desired sail angle
        """
        try:
            if not self.winches:
                return

            # Calculate sail position at desired angle
            sailPos = self.position + Vector(
                Angle(1, 180) + angle + self.position.angle,
                self.size
            )

            # Calculate distances from all winches
            d = [w.distance(sailPos) for w in self.winches]

            if not d:
                return

            # Set all winches to max distance (shorter cable would be impossible)
            max_distance = max(d)
            for w in self.winches:
                w.length = max_distance
                w.rot = angle

        except Exception as e:
            logger.error(f"Error setting sail rotation: {e}")
    

    def updateSailRotation(self, dt: float, wind: Vector) -> None:
        """
        Update sail rotation based on aerodynamic forces and winch constraints

        Args:
            dt: Time step (seconds)
            wind: Apparent wind vector
        """
        try:
            if not self.winches:
                return

            # Calculate total aerodynamic force
            forces = self.liftForce(wind) + self.dragForce(wind)

            # Center of effort distance (m)
            ce = 0.49

            # Calculate moment from aerodynamic forces
            # -1 is due to convention and format of apparent wind
            angle_rad = forces.angle.calc() * DEG_TO_RAD
            moment = -math.sin(angle_rad) * ce

            # Rotational inertia (kg⋅m²)
            rotInertia = 0.54

            # Angular acceleration (rad/s²)
            alpha = Validator.safe_divide(moment, rotInertia, default=0.0)

            # Update rotational velocity
            self.rotationalVelocity += alpha * dt

            # Calculate current and new positions
            pos1 = self.position + Vector(
                self.angle + self.position.angle + Angle(1, 180),
                self.size
            )

            # Calculate new angle using kinematic equation
            angle_change_rad = self.rotationalVelocity * dt + 0.5 * alpha * dt * dt
            angle_change_deg = angle_change_rad * RAD_TO_DEG
            angle2 = self.angle + Angle(1, angle_change_deg)

            pos2 = self.position + Vector(
                angle2 + self.position.angle + Angle(1, 180),
                self.size
            )

            # Check winch constraints
            for w in self.winches:
                dist1 = w.distance(pos1)
                dist2 = w.distance(pos2)

                # If sail hits winch length limit
                if dist1 >= w.length and dist1 <= dist2:
                    # Check if we need to flip winch rotation direction
                    angle_diff1 = abs(printA((self.angle - w.rot).calc()))
                    angle_diff2 = abs(printA((self.angle + w.rot).calc()))

                    if angle_diff1 > angle_diff2:
                        for n in self.winches:
                            n.rot = Angle(1, -n.rot.calc())

                    # Set sail angle to winch limit with small offset
                    if Angle.norm(w.rot).calc() > 0:
                        self.angle = w.rot - Angle(1, 2)
                    else:
                        self.angle = w.rot + Angle(1, 2)

                    # Stop rotation
                    self.rotationalVelocity = 0
                    alpha = 0

            # Update angle if still rotating
            if abs(self.rotationalVelocity) > EPSILON:
                self.angle = angle2

        except Exception as e:
            logger.error(f"Error updating sail rotation: {e}", exc_info=True)

    def read(self, datasheet: str, atr: str) -> List[Tuple[Angle, float]]:
        """
        Read coefficient data from file

        Args:
            datasheet: Path to data file
            atr: Attribute name to read (e.g., "Cl", "Cd", "CL", "CD")

        Returns:
            List of (angle, coefficient) tuples

        Raises:
            FoilDataError: If file cannot be read or attribute not found
        """
        try:
            units = []
            values = []

            with open(datasheet, "r") as sheet:
                if "naca" in datasheet.lower():
                    # NACA format: CSV with header row
                    line = sheet.readline()

                    # Find header row with "alpha" or "alfa"
                    while line and line.split(",")[0].lower() not in ["alpha", "alfa"]:
                        line = sheet.readline()

                    if not line:
                        raise FoilDataError(f"Could not find alpha column in {datasheet}")

                    # Parse header to find attribute column
                    line = line.replace('\n', "").replace('\r', "")
                    headers = line.split(",")

                    if atr not in headers:
                        raise FoilDataError(f"Attribute '{atr}' not found in {datasheet}")

                    idx = headers.index(atr)

                    # Read data rows
                    line = sheet.readline()
                    while line and len(line.strip()) > 1:
                        parts = line.split(",")
                        if len(parts) > idx:
                            try:
                                units.append(Angle(0, float(parts[0])))
                                values.append(float(parts[idx]))
                            except ValueError:
                                pass  # Skip invalid rows
                        line = sheet.readline()

                else:
                    # Standard format: space-separated
                    first_line = sheet.readline()

                    if "mainsailcoeffs" in datasheet.lower():
                        # Main sail coefficients use half angles
                        units = [Angle(0, float(x) // 2) for x in first_line.split()[1:]]
                    else:
                        units = [Angle(0, float(x)) for x in first_line.split()[1:]]

                    # Find attribute row
                    line = sheet.readline()
                    while line and line.split()[0] != atr:
                        line = sheet.readline()

                    if not line:
                        raise FoilDataError(f"Attribute '{atr}' not found in {datasheet}")

                    values = [float(x) for x in line.split()[1:]]

            if len(units) != len(values):
                raise FoilDataError(f"Mismatched units and values in {datasheet}")

            if not units:
                raise FoilDataError(f"No data found for '{atr}' in {datasheet}")

            logger.debug(f"Loaded {len(units)} {atr} coefficients from {datasheet}")
            return list(zip(units, values))

        except FileNotFoundError:
            raise FoilDataError(f"Data file not found: {datasheet}")
        except Exception as e:
            raise FoilDataError(f"Error reading {atr} from {datasheet}: {e}")

    def linearInterpolation(self, data_list: List[Tuple[Angle, float]], value: float) -> float:
        """
        Perform linear interpolation on coefficient data

        Args:
            data_list: List of (angle, coefficient) tuples
            value: Angle value to interpolate at

        Returns:
            Interpolated coefficient value
        """
        try:
            if not data_list:
                logger.warning("Empty data list for interpolation")
                return 0.0

            if len(data_list) == 1:
                return data_list[0][1]

            # Find bracketing indices
            idx = 0
            for i in range(len(data_list)):
                if data_list[i][0].data() > value:
                    idx = i
                    break
                idx = i

            # Clamp to valid range
            idx = max(0, idx - 1)
            idx = min(idx, len(data_list) - 2)

            # Linear interpolation
            x0 = data_list[idx][0].data()
            x1 = data_list[idx + 1][0].data()
            y0 = data_list[idx][1]
            y1 = data_list[idx + 1][1]

            # Safe division
            slope = Validator.safe_divide(y1 - y0, x1 - x0, default=0.0)
            result = slope * (value - x0) + y0

            return result

        except Exception as e:
            logger.error(f"Error in linear interpolation: {e}")
            return 0.0

    def cd(self, a: Angle) -> float:
        """
        Get drag coefficient at given angle

        Args:
            a: Angle

        Returns:
            Drag coefficient (dimensionless)
        """
        try:
            angle_val = abs(a.data())
            angle_val %= 360

            if not self.dragC:
                logger.warning("No drag coefficient data available")
                return 0.0

            last = self.dragC[-1][0].data()
            if angle_val > last:
                angle_val = last - (angle_val % last)

            return self.linearInterpolation(self.dragC, angle_val)

        except Exception as e:
            logger.error(f"Error getting drag coefficient: {e}")
            return 0.0

    def cl(self, a: Angle) -> float:
        """
        Get lift coefficient at given angle

        Args:
            a: Angle

        Returns:
            Lift coefficient (dimensionless)
        """
        try:
            angle_val = abs(a.data())
            angle_val %= 360

            if not self.liftC:
                logger.warning("No lift coefficient data available")
                return 0.0

            last = self.liftC[-1][0].data()
            if angle_val > last:
                angle_val = last - (angle_val % last)

            return self.linearInterpolation(self.liftC, angle_val)

        except Exception as e:
            logger.error(f"Error getting lift coefficient: {e}")
            return 0.0


class Winch:
    """
    Winch class for sail control

    Manages sail sheet length and position for sail trim control.
    """

    def __init__(self, position: Vector, length: float, radius: float):
        """
        Initialize winch

        Args:
            position: Position vector of winch
            length: Initial sheet length (m)
            radius: Winch radius (m)
        """
        try:
            self.position: Vector = position
            self.length: float = Validator.validate_positive(length, "winch length")
            self.radius: float = Validator.validate_positive(radius, "winch radius")
            self.rot: Angle = Angle(1, 0)  # Internal variable for display
        except Exception as e:
            logger.error(f"Error initializing winch: {e}")
            # Set safe defaults
            self.position = position
            self.length = abs(length) if length != 0 else 1.0
            self.radius = abs(radius) if radius != 0 else 0.1
            self.rot = Angle(1, 0)

    def setLength(self, length: float) -> None:
        """
        Set sheet length

        Args:
            length: New sheet length (m)
        """
        try:
            self.length = Validator.validate_positive(length, "winch length")
        except Exception as e:
            logger.warning(f"Invalid winch length {length}, keeping current: {e}")

    def distance(self, pos2: Vector) -> float:
        """
        Calculate distance to another position

        Args:
            pos2: Target position vector

        Returns:
            Distance in meters
        """
        try:
            dx = self.position.xcomp() - pos2.xcomp()
            dy = self.position.ycomp() - pos2.ycomp()
            dist = math.sqrt(dx * dx + dy * dy)

            if math.isnan(dist) or math.isinf(dist):
                logger.warning("Invalid distance calculated")
                return 0.0

            return dist

        except Exception as e:
            logger.error(f"Error calculating winch distance: {e}")
            return 0.0