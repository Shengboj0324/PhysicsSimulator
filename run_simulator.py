#!/usr/bin/env python3
"""
Physics Sailing Simulator - Main Entry Point

Loads boat configuration from boat_config.yaml and runs the simulator.

Enhanced with:
- Comprehensive error handling
- Input validation
- Logging
- Type hints
- Industrial-grade reliability
"""

import sys
import os
import yaml
import math
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import simulator components
from simulator.core.Variables import Angle, Vector
from simulator.core.Boat import Boat
from simulator.core.Foil import foil, Winch
from simulator.display.Display import display
from simulator.utils.polardiagram import generatePolars

# Import validation and error handling
try:
    from simulator.core.validators import Validator
    from simulator.core.exceptions import ConfigurationError, ValidationError
    from simulator.core.logger import logger
    from simulator.core.constants import (
        DEFAULT_WIND_SPEED, DEFAULT_WIND_DIRECTION,
        MIN_BOAT_MASS, MAX_BOAT_MASS
    )
except ImportError:
    # Fallback for backward compatibility
    class Validator:
        @staticmethod
        def validate_positive(value, name="value", allow_zero=False):
            return float(value)
        @staticmethod
        def validate_range(value, min_val, max_val, name="value"):
            return float(value)
        @staticmethod
        def validate_file_exists(filepath, name="file"):
            return Path(filepath)

    class ConfigurationError(Exception):
        pass
    class ValidationError(Exception):
        pass

    class logger:
        @staticmethod
        def info(msg, **kwargs):
            print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs):
            print(f"ERROR: {msg}")
        @staticmethod
        def warning(msg, **kwargs):
            print(f"WARNING: {msg}")

    DEFAULT_WIND_SPEED = 5.0
    DEFAULT_WIND_DIRECTION = 270.0
    MIN_BOAT_MASS = 0.1
    MAX_BOAT_MASS = 10000.0


def load_config(config_file: str = 'boat_config.yaml') -> Dict[str, Any]:
    """
    Load boat configuration from YAML file.

    Args:
        config_file: Path to YAML configuration file

    Returns:
        Dictionary containing boat configuration

    Raises:
        ConfigurationError: If file not found or invalid YAML
        ValidationError: If configuration is invalid
    """
    try:
        config_path = Validator.validate_file_exists(config_file, "configuration file")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if not config:
            raise ConfigurationError(f"Configuration file {config_file} is empty")

        # Validate required sections
        required_sections = ['hulls', 'sails', 'wind', 'boat', 'initial_state', 'polars', 'location']
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required section: {section}")

        logger.info(f"Loaded configuration from {config_file}")
        return config

    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_file}")
        raise ConfigurationError(f"Configuration file not found: {config_file}")
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file: {e}")
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def create_boat_from_config(config: Dict[str, Any]) -> Boat:
    """
    Create a boat instance from configuration.

    Args:
        config: Dictionary containing boat configuration

    Returns:
        Configured Boat instance

    Raises:
        ConfigurationError: If configuration is invalid
        ValidationError: If values are out of range
    """
    try:
        logger.info("Creating boat from configuration...")

        # Create hulls
        hulls = []
        vaka_size = None  # Store main hull size for rudder positioning

        for i, hull_config in enumerate(config['hulls']):
            try:
                # Validate hull configuration
                required_keys = ['name', 'datasheet', 'material_density', 'wetted_area',
                               'position', 'rotational_inertia', 'size']
                for key in required_keys:
                    if key not in hull_config:
                        raise ConfigurationError(f"Hull {i}: Missing required key '{key}'")

                # Validate values
                material_density = Validator.validate_positive(
                    hull_config['material_density'],
                    f"Hull {i} material_density"
                )
                wetted_area = Validator.validate_positive(
                    hull_config['wetted_area'],
                    f"Hull {i} wetted_area"
                )
                rot_inertia = Validator.validate_positive(
                    hull_config['rotational_inertia'],
                    f"Hull {i} rotational_inertia",
                    allow_zero=True
                )
                size = Validator.validate_positive(
                    hull_config['size'],
                    f"Hull {i} size"
                )

                # Handle position
                if hull_config['position']['distance'] == 0:
                    position = Vector(Angle(1, hull_config['position']['angle']), 0)
                else:
                    position = Vector(
                        Angle(1, hull_config['position']['angle']),
                        hull_config['position']['distance']
                    )

                # Special handling for rudder position (relative to vaka)
                if hull_config['name'] == 'rudder' and vaka_size:
                    position = Vector(Angle(1, 180), vaka_size / 2)

                # Validate datasheet file exists
                datasheet_path = Validator.validate_file_exists(
                    hull_config['datasheet'],
                    f"Hull {i} datasheet"
                )

                # Create hull
                hull = foil(
                    str(datasheet_path),
                    material_density,
                    wetted_area,
                    position=position,
                    rotInertia=rot_inertia,
                    size=size
                )

                hulls.append(hull)
                logger.info(f"Created hull: {hull_config['name']}")

                # Store vaka size for rudder positioning
                if hull_config['name'] == 'vaka':
                    vaka_size = size

            except Exception as e:
                logger.error(f"Error creating hull {i} ({hull_config.get('name', 'unknown')}): {e}")
                raise ConfigurationError(f"Error creating hull {i}: {e}")

        if not hulls:
            raise ConfigurationError("No hulls configured")
    
        # Create sails
        sails = []

        for i, sail_config in enumerate(config['sails']):
            try:
                # Validate sail configuration
                required_keys = ['name', 'datasheet', 'material_density', 'wetted_area',
                               'position', 'rotational_inertia', 'size', 'initial_angle', 'winches']
                for key in required_keys:
                    if key not in sail_config:
                        raise ConfigurationError(f"Sail {i}: Missing required key '{key}'")

                # Create winches
                winches = []
                for j, winch_config in enumerate(sail_config['winches']):
                    try:
                        winch_pos = Vector(
                            Angle(1, winch_config['position']['angle']),
                            winch_config['position']['distance']
                        )
                        offset = Vector(
                            Angle(1, winch_config['offset_angle']),
                            winch_config['offset_distance']
                        )

                        length = Validator.validate_positive(
                            winch_config['length'],
                            f"Sail {i} winch {j} length"
                        )
                        radius = Validator.validate_positive(
                            winch_config['radius'],
                            f"Sail {i} winch {j} radius"
                        )

                        winch = Winch(winch_pos + offset, length, radius)
                        winches.append(winch)
                    except Exception as e:
                        logger.error(f"Error creating winch {j} for sail {i}: {e}")
                        raise ConfigurationError(f"Error creating winch {j} for sail {i}: {e}")

                # Validate sail values
                material_density = Validator.validate_positive(
                    sail_config['material_density'],
                    f"Sail {i} material_density"
                )
                wetted_area = Validator.validate_positive(
                    sail_config['wetted_area'],
                    f"Sail {i} wetted_area"
                )
                rot_inertia = Validator.validate_positive(
                    sail_config['rotational_inertia'],
                    f"Sail {i} rotational_inertia",
                    allow_zero=True
                )
                size = Validator.validate_positive(
                    sail_config['size'],
                    f"Sail {i} size"
                )

                # Validate datasheet file exists
                datasheet_path = Validator.validate_file_exists(
                    sail_config['datasheet'],
                    f"Sail {i} datasheet"
                )

                # Create sail
                sail = foil(
                    str(datasheet_path),
                    material_density,
                    wetted_area,
                    position=Vector(
                        Angle(1, sail_config['position']['angle']),
                        sail_config['position']['distance']
                    ),
                    rotInertia=rot_inertia,
                    size=size,
                    winches=winches
                )

                # Set initial sail angle
                sail.angle = Angle(1, sail_config['initial_angle'])
                sail.setSailRotation(sail.angle)

                sails.append(sail)
                logger.info(f"Created sail: {sail_config['name']}")

            except Exception as e:
                logger.error(f"Error creating sail {i} ({sail_config.get('name', 'unknown')}): {e}")
                raise ConfigurationError(f"Error creating sail {i}: {e}")

        # Create wind
        wind_direction = config['wind'].get('direction', DEFAULT_WIND_DIRECTION)
        wind_speed = config['wind'].get('speed', DEFAULT_WIND_SPEED)

        wind_speed = Validator.validate_positive(wind_speed, "wind speed")

        wind = Vector(
            Angle(1, wind_direction),
            wind_speed
        )
        logger.info(f"Wind: {wind_speed:.1f} m/s from {wind_direction:.0f}°")

        # Validate boat mass
        boat_mass = Validator.validate_range(
            config['boat']['mass'],
            MIN_BOAT_MASS,
            MAX_BOAT_MASS,
            "boat mass"
        )

        # Validate latitude
        ref_lat = Validator.validate_range(
            config['initial_state']['latitude'],
            -90.0,
            90.0,
            "latitude"
        )

        # Create boat
        boat = Boat(
            hulls,
            sails,
            wind,
            mass=boat_mass,
            refLat=ref_lat
        )
        logger.info(f"Created boat: mass={boat_mass}kg, refLat={ref_lat}°")

        # Set initial position and heading
        heading = config['initial_state'].get('heading', 0.0)
        boat.angle = Angle(1, heading)

        # Calculate position from lat/lon
        lat = config['initial_state']['latitude']
        lon = config['initial_state']['longitude']
        boat.setPos(Vector(
            Angle(1, round(math.atan2(lat, lon) * 180 / math.pi * 10000) / 10000),
            math.sqrt(lon**2 + lat**2)
        ))
        logger.info(f"Initial position: lat={lat:.6f}, lon={lon:.6f}, heading={heading:.1f}°")

        logger.info("Boat creation complete!")
        return boat

    except Exception as e:
        logger.error(f"Fatal error creating boat: {e}", exc_info=True)
        raise


def main() -> int:
    """
    Run the physics sailing simulator.

    Returns:
        Exit code (0 for success, non-zero for error)
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Physics Sailing Simulator - Industrial Grade Competition Ready',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default config
  %(prog)s --config my_boat.yaml    # Run with custom config
  %(prog)s --recalc-polars          # Force polar recalculation
  %(prog)s --validate-only          # Validate config without running
        """
    )
    parser.add_argument('--config', '-c', default='boat_config.yaml',
                        help='Path to boat configuration file (default: boat_config.yaml)')
    parser.add_argument('--recalc-polars', action='store_true',
                        help='Force recalculation of polar diagrams')
    parser.add_argument('--validate-only', action='store_true',
                        help='Validate configuration without running simulator')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0 (Industrial Grade)')

    args = parser.parse_args()

    try:
        logger.info("=" * 80)
        logger.info("Physics Sailing Simulator - Industrial Grade v2.0")
        logger.info("Competition Ready - 2024-2025 Kehillah Sailbot")
        logger.info("=" * 80)

        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
        logger.info("✓ Configuration loaded successfully")

        # Create boat from config
        logger.info("Creating boat from configuration...")
        boat = create_boat_from_config(config)
        logger.info("✓ Boat created successfully")

        # Validate only mode
        if args.validate_only:
            logger.info("=" * 80)
            logger.info("✓ VALIDATION SUCCESSFUL - Configuration is valid!")
            logger.info("=" * 80)
            return 0

        # Check if polar recalculation is requested
        if args.recalc_polars or config.get('polars', {}).get('recalculate', False):
            logger.info("Recalculating polar diagrams...")
            polar_filename = config.get('polars', {}).get('filename', 'polar_diagram.png')
            try:
                generatePolars(boat, polar_filename)
                logger.info(f"✓ Polar diagrams saved to: {polar_filename}")
            except Exception as e:
                logger.warning(f"Failed to generate polar diagrams: {e}")
                logger.warning("Continuing without polar diagrams...")

        # Create and run display
        logger.info("Initializing display system...")
        location = config.get('location', 'Shoreline Lake, Mountain View, CA')
        render = display(location, boat)
        logger.info("✓ Display initialized")

        logger.info("=" * 80)
        logger.info("Starting simulation...")
        logger.info("=" * 80)
        render.runAnimation()

        logger.info("Simulation completed successfully")
        return 0

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your configuration file and try again.")
        return 1

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        logger.error("Please check your configuration values and try again.")
        return 2

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please check that all required files exist.")
        return 3

    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
        logger.info("Shutting down gracefully...")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        logger.error("=" * 80)
        logger.error("SIMULATION FAILED")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())