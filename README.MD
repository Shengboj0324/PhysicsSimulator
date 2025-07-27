# Physics Sailing Simulator

A comprehensive sailing simulation with realistic physics and modular controller architecture for easy development and testing of navigation algorithms.

**Kehillah Sailbot boat simulation program for the 2024-2025 Sailbot competition**

## Quick Start

```bash
# Run with default configuration
python3 run_simulator.py

# Run with custom boat configuration
python3 run_simulator.py --config boat_config_simple.yaml

# Force recalculation of polar diagrams
python3 run_simulator.py --recalc-polars
```

## Main Features

- **Realistic Physics**: Aerodynamic and hydrodynamic forces on boat sails and hulls
- **Navigation Testing**: Test navigation algorithms with accurate boat behavior
- **Performance Optimization**: Calculate optimal sail trim, best VMG, and headings
- **Modular Controllers**: Easy-to-develop custom control algorithms
- **YAML Configuration**: Simple boat setup without code changes

## Project Structure

```
PhysicsSimulator/
├── simulator/                  # Main simulator package
│   ├── core/                  # Physics simulation core
│   ├── display/               # Visualization system
│   ├── control/               # Control systems
│   │   ├── controllers/       # Modular controllers
│   │   └── algorithms/        # Navigation algorithms
│   └── utils/                 # Utility functions
├── data/                      # Boat performance data
├── docs/                      # Documentation
├── boat_config.yaml           # Default boat configuration
├── boat_config_simple.yaml    # Simple example configuration
└── run_simulator.py           # Main entry point
```

## Configuration

Boats are configured using YAML files. See `boat_config.yaml` for a complete example.

### Simple Example

```yaml
location: "Newport, Rhode Island"

wind:
  direction: 90   # From East
  speed: 10       # m/s

hulls:
  - name: "main_hull"
    datasheet: "data/naca0015-R7e7-F180.csv"
    material_density: 1000    # Water
    wetted_area: 0.5
    size: 2.0
    position:
      angle: 0
      distance: 0

sails:
  - name: "main_sail"
    datasheet: "data/mainSailCoeffs.cvs"
    material_density: 1.204   # Air
    wetted_area: 10.0
    size: 5.0
    position:
      angle: 0
      distance: 0
```

See [docs/README_CONFIG.md](docs/README_CONFIG.md) for detailed configuration guide.

## Creating Custom Controllers

The modular system allows easy development of custom control algorithms:

```python
from simulator.control.controllers import BaseRudderController

class MyRudderController(BaseRudderController):
    def calculate_rudder_angle(self, target_heading=None, **kwargs):
        # Your custom steering logic
        return rudder_angle  # -10 to +10 degrees
```

See [simulator/docs/MODULAR_CONTROLLER_README.md](simulator/docs/MODULAR_CONTROLLER_README.md) for details.

## Physics & Conventions

### Units
- **Forces**: Newtons
- **Distance**: Meters  
- **Angles**: Degrees
- **Density**: kg/m³

### Angle Conventions
- **Wind**: Direction wind is coming FROM (0° = East wind blowing West)
- **Calculation angles**: Unit circle (0° = East, 90° = North)
- **Data angles**: 0-180° range for foil data

### Core Classes
- **Variable**: Base class for angles and vectors with automatic unit conversion
- **Foil**: Calculates lift and drag forces on sails/hulls
- **Boat**: Manages foils, position, velocity, and force calculations

## Development

### Requirements
- Python 3.7+
- matplotlib
- numpy
- pyyaml
- Additional dependencies in `requirements.txt`

### Installation
```bash
pip install -r requirements.txt
python3 run_simulator.py
```

## Documentation

- [Configuration Guide](docs/README_CONFIG.md) - Detailed YAML configuration
- [Modular Controllers](simulator/docs/MODULAR_CONTROLLER_README.md) - Creating custom controllers
- [Control Algorithms](simulator/control/algorithms/README.md) - Available algorithms

## TODO

- Improve sail physics for realistic jibes and tacks
- Fix variable system display/data angle issues
- Add more sophisticated control algorithms

## Citations

- Boeing, G. 2017. ["OSMnx: New Methods for Acquiring, Constructing, Analyzing, and Visualizing Complex Street Networks."](https://geoffboeing.com/publications/osmnx-complex-street-networks/) Computers, Environment and Urban Systems 65, 126-139.

---

*This is the third iteration of the Kehillah Sailbot boat simulation program*