# Modular Controller System

This refactoring introduces a modular controller system that separates control logic into pluggable components, making it easy to develop and test new control algorithms.

## Overview

The modular system abstracts three key control functions:
- **Rudder Control**: Determines rudder angle based on navigation goals
- **Sail Control**: Optimizes sail trim based on wind conditions  
- **Pathfinding**: Plans routes between waypoints, handling no-go zones

## Architecture

### Base Classes

All custom controllers inherit from these base classes:

- `BaseRudderController`: Interface for rudder control algorithms
- `BaseSailController`: Interface for sail trim algorithms
- `BasePathfindingController`: Interface for pathfinding algorithms

### Default Implementations

The system includes default implementations extracted from the original code:

- `SimpleRudderController`: Proportional control with velocity damping
- `WaypointRudderController`: Steers toward waypoints
- `SimpleSailController`: Uses angle of attack optimization
- `SimplePathfindingController`: Handles tacking and jibing

## Creating Custom Controllers

### 1. Rudder Controller Example

```python
from controllers import BaseRudderController

class CustomRudderController(BaseRudderController):
    def calculate_rudder_angle(self, target_heading=None, **kwargs):
        # Your custom rudder logic here
        return rudder_angle  # -10 to +10 degrees
```

### 2. Sail Controller Example

```python
from controllers import BaseSailController

class CustomSailController(BaseSailController):
    def calculate_sail_angle(self, apparent_wind_angle, **kwargs):
        # Your custom sail trim logic here
        return sail_angle  # degrees
```

### 3. Pathfinding Controller Example

```python
from controllers import BasePathfindingController

class CustomPathfindingController(BasePathfindingController):
    def calculate_path(self, start_point, end_point, wind_direction, **kwargs):
        # Your custom pathfinding logic here
        return waypoint_list  # [[x, y], [x, y], ...]
    
    def check_waypoint_arrival(self, position, target_waypoint, **kwargs):
        # Your arrival detection logic here
        return arrived  # True/False
```

## Using the Modular System

### Basic Usage with Defaults

```python
from ControlModular import ModularController

# Uses default controllers
controller = ModularController(boat)
```

### Using Custom Controllers

```python
# Use custom controllers
controller = ModularController(
    boat,
    rudder_controller=MyRudderController(boat),
    sail_controller=MySailController(boat),
    pathfinding_controller=MyPathfindingController(boat, controller)
)
```

### Runtime Controller Switching

```python
# Switch controllers during operation
controller.set_rudder_controller(AnotherRudderController(boat))
controller.set_sail_controller(AnotherSailController(boat))
```

## File Organization

```
PhysicsSimulator/
├── controllers/                 # Modular controller system
│   ├── base_controllers.py     # Abstract base classes
│   ├── rudder/                 # Rudder control implementations
│   │   ├── simple_rudder.py
│   │   └── custom_rudder.py    # Your custom controllers
│   ├── sail/                   # Sail control implementations
│   │   ├── simple_sail.py
│   │   └── custom_sail.py
│   └── pathfinding/            # Pathfinding implementations
│       ├── simple_pathfinding.py
│       └── custom_pathfinding.py
├── ControlModular.py           # Main modular controller
├── example_modular.py          # Usage examples
├── Display.py                  # Original display (unchanged)
├── Boat.py                     # Original boat physics (unchanged)
└── ...
```

## Testing Your Controllers

1. Create your custom controller file
2. Import it in your main script
3. Pass it to `ModularController`
4. Run the simulation to test

Example:
```python
python3 example_modular.py
```

## Benefits

- **Modularity**: Each control aspect is separate and replaceable
- **Testability**: Easy to test individual controllers in isolation
- **Extensibility**: Add new controller types without modifying core code
- **Reusability**: Controllers can be mixed and matched
- **Compatibility**: Existing Display.py system remains unchanged

## Backward Compatibility

The original `Control.py` and `Display.py` remain untouched. The modular system is additive and can coexist with the original system.

## Next Steps

1. Test the modular system with the existing simulator
2. Create additional controller implementations
3. Integrate with the display system for seamless usage
4. Add more sophisticated pathfinding algorithms
5. Implement machine learning-based controllers