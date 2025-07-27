#!/usr/bin/env python3
"""
Physics Sailing Simulator - Main Entry Point

Loads boat configuration from boat_config.yaml and runs the simulator.
"""

import sys
import os
import yaml
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator'))

from simulator.core.Variables import Angle, Vector
from simulator.core.Boat import Boat
from simulator.core.Foil import foil, Winch
from simulator.display.Display import display
from simulator.utils.polardiagram import generatePolars


def load_config(config_file='boat_config.yaml'):
    """Load boat configuration from YAML file."""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def create_boat_from_config(config):
    """Create a boat instance from configuration."""
    
    # Create hulls
    hulls = []
    vaka_size = None  # Store main hull size for rudder positioning
    
    for hull_config in config['hulls']:
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
        
        # Create hull
        hull = foil(
            hull_config['datasheet'],
            hull_config['material_density'],
            hull_config['wetted_area'],
            position=position,
            rotInertia=hull_config['rotational_inertia'],
            size=hull_config['size']
        )
        
        hulls.append(hull)
        
        # Store vaka size for rudder positioning
        if hull_config['name'] == 'vaka':
            vaka_size = hull_config['size']
    
    # Create sails
    sails = []
    
    for sail_config in config['sails']:
        # Create winches
        winches = []
        for winch_config in sail_config['winches']:
            winch_pos = Vector(
                Angle(1, winch_config['position']['angle']),
                winch_config['position']['distance']
            )
            offset = Vector(
                Angle(1, winch_config['offset_angle']),
                winch_config['offset_distance']
            )
            winch = Winch(
                winch_pos + offset,
                winch_config['length'],
                winch_config['radius']
            )
            winches.append(winch)
        
        # Create sail
        sail = foil(
            sail_config['datasheet'],
            sail_config['material_density'],
            sail_config['wetted_area'],
            position=Vector(
                Angle(1, sail_config['position']['angle']),
                sail_config['position']['distance']
            ),
            rotInertia=sail_config['rotational_inertia'],
            size=sail_config['size'],
            winches=winches
        )
        
        # Set initial sail angle
        sail.angle = Angle(1, sail_config['initial_angle'])
        sail.setSailRotation(sail.angle)
        
        sails.append(sail)
    
    # Create wind
    wind = Vector(
        Angle(1, config['wind']['direction']),
        config['wind']['speed']
    )
    
    # Create boat
    boat = Boat(
        hulls,
        sails,
        wind,
        mass=config['boat']['mass'],
        refLat=config['initial_state']['latitude']
    )
    
    # Set initial position and heading
    boat.angle = Angle(1, config['initial_state']['heading'])
    
    # Calculate position from lat/lon
    lat = config['initial_state']['latitude']
    lon = config['initial_state']['longitude']
    boat.setPos(Vector(
        Angle(1, round(math.atan2(lat, lon) * 180 / math.pi * 10000) / 10000),
        math.sqrt(lon**2 + lat**2)
    ))
    
    return boat


def main():
    """Run the physics sailing simulator."""
    
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Physics Sailing Simulator')
    parser.add_argument('--config', '-c', default='boat_config.yaml',
                        help='Path to boat configuration file (default: boat_config.yaml)')
    parser.add_argument('--recalc-polars', action='store_true',
                        help='Force recalculation of polar diagrams')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create boat from config
    boat = create_boat_from_config(config)
    
    # Check if polar recalculation is requested
    if args.recalc_polars or config['polars']['recalculate']:
        print("Recalculating polar diagrams...")
        generatePolars(boat, config['polars']['filename'])
    
    # Create and run display
    render = display(config['location'], boat)
    render.runAnimation()


if __name__ == "__main__":
    main()