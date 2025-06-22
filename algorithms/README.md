# Custom Control Algorithms

This directory contains custom control algorithms for the physics simulator.

## How to Create a New Algorithm

1. **Copy the template:**
   ```bash
   cp template_algorithm.py my_algorithm.py
   ```

2. **Edit your algorithm:**
   - Rename the class from `TemplateAlgorithm` to your algorithm name
   - Implement your control logic in the `update()` method
   - Use `self.boat` to access boat state
   - Use `self.controller` to control the boat

3. **Configure the simulator to use your algorithm:**
   Edit `simulator_config.py`:
   ```python
   from algorithms.my_algorithm import MyAlgorithm
   CONTROL_ALGORITHM = MyAlgorithm
   ```

4. **Run the simulator:**
   ```bash
   python Display.py
   ```
   Click "Auto Pilot: OFF" to activate your algorithm.

## Example Algorithms

- **beam_reach_algorithm.py** - Maintains a beam reach (90° to wind)
- **close_hauled_algorithm.py** - Sails as close to wind as possible
- **compass_heading_algorithm.py** - Maintains a specific compass heading

## Available Boat Data

In your `update()` method, you can access:

```python
# Position and velocity
self.boat.position              # Current position vector
self.boat.linearVelocity       # Current velocity vector
self.boat.angle.calc()         # Current heading in degrees
self.boat.rotationalVelocity   # Angular velocity in rad/s

# Wind information
self.boat.wind.angle.calc()    # Wind direction in degrees
self.boat.wind.norm            # Wind speed
self.boat.globalAparentWind()  # Apparent wind vector

# Hull and sail information
self.boat.hulls                # List of hull objects
self.boat.sails                # List of sail objects
```

## Control Methods

To control the boat:

```python
# Steer the boat
self.controller.updateRudderAngle(noise, stability, target_angle)

# Adjust sails automatically
self.controller.updateSails()

# Access navigation methods
self.controller.leg(start, stop)  # Calculate path between points
self.controller.VB(angle, wind)   # Get boat speed from polars
```

## Tips

- Start simple - test basic heading control first
- Use `print()` statements to debug your algorithm
- The simulator runs at 70 fps, so `dt` is typically 1/70 seconds
- Wind angle 0° is North, 90° is East, etc.
- Boat angle follows the same convention