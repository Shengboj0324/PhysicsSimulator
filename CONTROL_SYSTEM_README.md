# Physics Simulator Control System

## Overview

The control system has been refactored to provide a modular, extensible architecture for implementing and testing different boat control algorithms. The wind angle is now properly integrated into all control calculations.

## Architecture

### Core Components

1. **Control.py** - Main controller that manages algorithms and basic navigation
2. **control_algorithms.py** - Modular control algorithm implementations
3. **navigation_utils.py** - Common navigation utilities and calculations
4. **station_keeping.py** - Specialized station keeping behavior

### Control Algorithms

#### Base Class: `ControlAlgorithm`
All control algorithms inherit from this abstract base class and must implement:
- `update(dt)` - Main control loop
- `get_state_info()` - Debug/status information

#### Available Algorithms

1. **WaypointFollowingAlgorithm** - Standard waypoint navigation
   - Supports endurance and precision courses
   - Automatic path recalculation
   - Handles tacking and jibing

2. **StationKeepingAlgorithm** - Maintains position within boundaries
   - Drift with wind direction
   - Return to upwind position when needed
   - State machine: ENTERING → REACHING_UPWIND → DRIFTING → RETURNING

3. **DirectControlAlgorithm** - Manual heading control
   - Set specific target heading
   - Useful for testing and debugging

4. **VMGOptimizationAlgorithm** - Velocity Made Good optimization
   - Finds optimal heading for best progress toward target
   - Considers boat polars and wind angle

## Usage Examples

### Basic Setup
```python
from Control import Controler

# Create controller
controller = Controler(boat, polars="test.pol")

# Plan a course (automatically selects appropriate algorithm)
controller.plan("e", waypoints)  # Endurance
controller.plan("s", waypoints)  # Station keeping
controller.plan("p", waypoints)  # Precision
```

### Custom Algorithm
```python
from control_algorithms import DirectControlAlgorithm

# Create custom algorithm
algo = DirectControlAlgorithm(boat, controller)
algo.set_target_heading(45)  # Head northeast

# Set it as active algorithm
controller.set_algorithm(algo)
```

### Creating New Algorithms
```python
from control_algorithms import ControlAlgorithm

class MyCustomAlgorithm(ControlAlgorithm):
    def update(self, dt):
        # Your control logic here
        target_angle = self.calculate_target()
        self.controller.updateRudderAngle(2, 1, target_angle)
        self.controller.updateSails()
        
    def get_state_info(self):
        return {"algorithm": "My Custom", "state": "Running"}
```

## Wind Integration

All control algorithms now properly use wind angle for calculations:

- **Relative Wind**: Calculated as `wind_angle - boat_heading`
- **No-Go Zones**: Automatically handled in path planning
- **Sail Trim**: Optimized based on apparent wind angle
- **Tacking/Jibing**: Triggered when crossing wind lines

## Navigation Utilities

Common functions available in `navigation_utils.py`:

- `normalize_angle(angle)` - Convert to [-180, 180] range
- `calculate_bearing(from, to)` - Get bearing between points
- `calculate_distance(p1, p2)` - Distance between points
- `is_upwind(bearing, wind)` - Check if in no-go zone
- `calculate_vmg(speed, heading, target)` - Velocity made good
- `optimal_tack_angles(wind, polars)` - Best tacking angles

## Testing Different Algorithms

See `control_examples.py` for demonstrations of:
- Switching algorithms at runtime
- Custom algorithm implementation
- Race tactics with laylines
- Wind-following behavior

## Key Improvements

1. **Modularity**: Easy to add new control algorithms
2. **Wind Integration**: All calculations properly use wind angle
3. **Clean Separation**: Navigation utilities separated from control logic
4. **Extensibility**: Simple interface for custom algorithms
5. **Maintainability**: Clear structure and documentation