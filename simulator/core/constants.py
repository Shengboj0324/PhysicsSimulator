"""
Physical and mathematical constants for the Physics Sailing Simulator

This module centralizes all constants to eliminate magic numbers and
improve code maintainability.
"""

import math

# ============================================================================
# MATHEMATICAL CONSTANTS
# ============================================================================

PI = math.pi
TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi

# Numerical precision
EPSILON = 1e-10  # Small number for floating point comparisons
ZERO_THRESHOLD = 1e-10  # Threshold for considering a value as zero

# ============================================================================
# GEOGRAPHIC CONSTANTS
# ============================================================================

# Earth radius in meters (mean radius)
EARTH_RADIUS_M = 6371000.0

# Meters per degree at equator
METERS_PER_DEGREE_EQUATOR = 111320.0

# Approximate meters per degree latitude (constant)
METERS_PER_DEGREE_LAT = 111111.0

# Approximate meters per degree longitude at mid-latitudes
# This varies with latitude, but 111.32 km is a reasonable approximation
METERS_PER_DEGREE_LON_APPROX = 111320.0

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

# Fluid densities (kg/m³)
WATER_DENSITY = 997.77  # Fresh water at 25°C
AIR_DENSITY = 1.204  # Air at sea level, 20°C

# Gravitational acceleration (m/s²)
GRAVITY = 9.81

# ============================================================================
# ANGLE TYPE CONSTANTS
# ============================================================================

# Angle types for the Variable system
ANGLE_TYPE_DATA = 0  # Data angles: 0-180° range for foil data
ANGLE_TYPE_CALC = 1  # Calc angles: Unit circle (0° = East, 90° = North)
ANGLE_TYPE_DISPLAY = 2  # Display angles: 0-360° with negatives allowed

# ============================================================================
# SAILING CONSTANTS
# ============================================================================

# No-go zones (degrees from wind direction)
DEFAULT_UPWIND_NO_GO_ANGLE = 45.0  # Cannot sail closer than 45° to wind
DEFAULT_DOWNWIND_NO_GO_ANGLE = 30.0  # Dead downwind zone

# Tacking and jibing angles
DEFAULT_TACK_ANGLE = 45.0  # Angle to sail when tacking upwind
DEFAULT_JIBE_ANGLE = 150.0  # Angle to sail when jibing downwind

# Sail control
DEFAULT_SAIL_MIN_ANGLE = 0.0  # Minimum sail angle (degrees)
DEFAULT_SAIL_MAX_ANGLE = 90.0  # Maximum sail angle (degrees)

# Rudder control
DEFAULT_RUDDER_MIN_ANGLE = -10.0  # Maximum left rudder (degrees)
DEFAULT_RUDDER_MAX_ANGLE = 10.0  # Maximum right rudder (degrees)
RUDDER_PHYSICAL_LIMIT = 45.0  # Absolute physical limit

# ============================================================================
# CONTROL SYSTEM CONSTANTS
# ============================================================================

# PID-like control parameters
DEFAULT_HEADING_ERROR_SCALE = 40.0  # Degrees
DEFAULT_STABILITY_FACTOR = 1.0
DEFAULT_NOISE_FACTOR = 2.0

# Waypoint navigation
DEFAULT_WAYPOINT_ARRIVAL_RADIUS = 5.0  # meters
DEFAULT_PATH_RECALC_INTERVAL = 1.0  # seconds

# Station keeping
DEFAULT_STATION_KEEPING_OUTER_BOX = 20.0  # meters
DEFAULT_STATION_KEEPING_INNER_BOX = 10.0  # meters
DEFAULT_STATION_KEEPING_DRIFT_RADIUS = 10.0  # meters

# ============================================================================
# PHYSICS SIMULATION CONSTANTS
# ============================================================================

# Time stepping
DEFAULT_TIMESTEP = 0.03  # seconds (33.3 fps)
DEFAULT_SUB_ITERATIONS = 30  # Sub-iterations per timestep for accuracy

# Physical limits (for validation and safety)
MAX_REALISTIC_BOAT_SPEED = 50.0  # m/s (~97 knots, faster than any sailboat)
MAX_REALISTIC_WIND_SPEED = 100.0  # m/s (~194 knots, hurricane force)
MAX_REALISTIC_ANGULAR_VELOCITY = 10.0  # rad/s
MAX_REALISTIC_FORCE = 10000.0  # Newtons
MAX_REALISTIC_MOMENT = 10000.0  # Newton-meters

# Minimum values for physical properties
MIN_BOAT_MASS = 0.1  # kg
MIN_WETTED_AREA = 0.001  # m²
MIN_ROTATIONAL_INERTIA = 0.001  # kg⋅m²

# ============================================================================
# DISPLAY CONSTANTS
# ============================================================================

# Frame rate and animation
DEFAULT_FPS = 70
DEFAULT_UPDATE_INTERVAL = 1  # frames between updates

# Visualization sizes (in degrees for map coordinates)
BUOY_RADIUS_METERS = 0.4  # Outer box buoy radius
INNER_BUOY_RADIUS_METERS = 0.2  # Inner box buoy radius
TARGET_POINT_RADIUS_METERS = 0.3  # Target point marker radius

# Arrow and line widths
FORCE_ARROW_WIDTH = 2.0
VELOCITY_ARROW_WIDTH = 2.0
COURSE_LINE_WIDTH = 1.5

# ============================================================================
# FILE AND DATA CONSTANTS
# ============================================================================

# Default file paths
DEFAULT_DATA_DIR = "data"
DEFAULT_LOG_DIR = "logs"
DEFAULT_CONFIG_FILE = "boat_config.yaml"
DEFAULT_SIMULATOR_CONFIG_FILE = "simulator_config.yaml"

# Polar diagram file extension
POLAR_FILE_EXTENSION = ".pol"
DEFAULT_POLAR_FILE = "data/test.pol"

# ============================================================================
# WIND AND WEATHER CONSTANTS
# ============================================================================

# Default wind conditions
DEFAULT_WIND_SPEED = 5.0  # m/s (~10 knots, light breeze)
DEFAULT_WIND_DIRECTION = 270.0  # degrees (from West)

# Wind speed ranges (Beaufort scale approximations)
WIND_CALM_MAX = 0.5  # m/s
WIND_LIGHT_AIR_MAX = 1.5  # m/s
WIND_LIGHT_BREEZE_MAX = 3.3  # m/s
WIND_GENTLE_BREEZE_MAX = 5.5  # m/s
WIND_MODERATE_BREEZE_MAX = 7.9  # m/s
WIND_FRESH_BREEZE_MAX = 10.7  # m/s
WIND_STRONG_BREEZE_MAX = 13.8  # m/s
WIND_NEAR_GALE_MAX = 17.1  # m/s
WIND_GALE_MAX = 20.7  # m/s
WIND_STRONG_GALE_MAX = 24.4  # m/s
WIND_STORM_MAX = 28.4  # m/s
WIND_VIOLENT_STORM_MAX = 32.6  # m/s

# ============================================================================
# BOAT CONFIGURATION CONSTANTS
# ============================================================================

# Boat mass limits
MAX_BOAT_MASS = 10000.0  # kg (10 tons, very large sailboat)

# Hull dimensions
MIN_HULL_SIZE = 0.1  # meters
MAX_HULL_SIZE = 100.0  # meters

# Sail dimensions
MIN_SAIL_AREA = 0.1  # m²
MAX_SAIL_AREA = 1000.0  # m²

# ============================================================================
# NAVIGATION AND PATHFINDING CONSTANTS
# ============================================================================

# Waypoint distances
MIN_WAYPOINT_DISTANCE = 0.1  # meters
MAX_WAYPOINT_DISTANCE = 10000.0  # meters (10 km)

# Path recalculation
DEFAULT_RECALC_INTERVAL = 1.0  # seconds

# Station keeping
MIN_DRIFT_RADIUS = 1.0  # meters
MAX_DRIFT_RADIUS = 100.0  # meters
DEFAULT_BOX_HALF_SIZE = 10.0  # meters

# ============================================================================
# ANIMATION AND DISPLAY CONSTANTS
# ============================================================================

# Animation timing
DEFAULT_ANIMATION_INTERVAL = 1  # milliseconds between frames
MIN_FPS = 1
MAX_FPS = 120

# CSV file parameters
CSV_DELIMITER = ","
CSV_COMMENT_CHAR = "#"

# ============================================================================
# COURSE TYPE CONSTANTS
# ============================================================================

COURSE_TYPE_PRECISION = "p"  # Precision navigation
COURSE_TYPE_ENDURANCE = "e"  # Endurance race
COURSE_TYPE_STATION_KEEPING = "s"  # Station keeping

# ============================================================================
# LOGGING CONSTANTS
# ============================================================================

LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# Performance thresholds for logging
SLOW_OPERATION_THRESHOLD = 0.1  # seconds (100ms)
VERY_SLOW_OPERATION_THRESHOLD = 1.0  # seconds

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

# Latitude and longitude ranges
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0

# Angle normalization ranges
ANGLE_RANGE_0_360 = (0.0, 360.0)
ANGLE_RANGE_NEG180_180 = (-180.0, 180.0)
ANGLE_RANGE_0_180 = (0.0, 180.0)

# ============================================================================
# COMPETITION CONSTANTS (Sailbot)
# ============================================================================

# Precision navigation course
PRECISION_COURSE_OFFSET = 1.5  # meters
PRECISION_COURSE_LEG_LENGTH = 25.0  # meters

# Endurance course
ENDURANCE_COURSE_WIDTH = 50.0  # meters (25m each side)
ENDURANCE_COURSE_LENGTH = 15.0  # meters

# Station keeping
STATION_KEEPING_OFFSET = 50.0  # meters from start position

# ============================================================================
# FOIL DATA CONSTANTS
# ============================================================================

# Interpolation
FOIL_DATA_INTERPOLATION_METHOD = "linear"

# Angle of attack limits (typical for NACA airfoils)
MIN_ANGLE_OF_ATTACK = -180.0
MAX_ANGLE_OF_ATTACK = 180.0

# ============================================================================
# WINCH CONSTANTS
# ============================================================================

DEFAULT_WINCH_LENGTH = 30.0  # meters
DEFAULT_WINCH_RADIUS = 0.025  # meters

# ============================================================================
# VECTOR CONSTANTS
# ============================================================================

# Unit vectors
UNIT_VECTOR_X = (1.0, 0.0)
UNIT_VECTOR_Y = (0.0, 1.0)

# Zero vector
ZERO_VECTOR = (0.0, 0.0)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_angle_0_360(angle: float) -> float:
    """Normalize angle to [0, 360) range"""
    return angle % 360.0


def normalize_angle_neg180_180(angle: float) -> float:
    """Normalize angle to [-180, 180) range"""
    angle = angle % 360.0
    if angle >= 180.0:
        angle -= 360.0
    return angle


def is_zero(value: float, threshold: float = ZERO_THRESHOLD) -> bool:
    """Check if value is effectively zero"""
    return abs(value) < threshold


def safe_acos(value: float) -> float:
    """Safe arccos that clamps input to [-1, 1]"""
    return math.acos(max(-1.0, min(1.0, value)))


def safe_asin(value: float) -> float:
    """Safe arcsin that clamps input to [-1, 1]"""
    return math.asin(max(-1.0, min(1.0, value)))

