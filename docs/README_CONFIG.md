# Boat Configuration Guide

The Physics Sailing Simulator uses YAML configuration files to define boat setups, making it easy to create and modify boat designs without changing code.

## Quick Start

```bash
# Run with default configuration
python3 run_simulator.py

# Run with a specific configuration
python3 run_simulator.py --config boat_config_simple.yaml
```

## Configuration Structure

### Basic Structure

```yaml
# Location for map display
location: "Location name"

# Wind settings
wind:
  direction: 270  # degrees (0=North, 90=East, 180=South, 270=West)
  speed: 5.3      # meters per second

# Initial boat state
initial_state:
  latitude: 37.431749
  longitude: -122.09064
  heading: -93    # degrees

# Hull configurations
hulls:
  - name: "hull_name"
    datasheet: "data/foil_data.csv"  # Aerodynamic data file
    material_density: 997.77          # kg/m³ (water=~1000, air=~1.2)
    wetted_area: 0.5                  # m²
    rotational_inertia: 1.0
    size: 2.0                         # meters
    position:
      angle: 0                        # degrees relative to boat center
      distance: 0                     # meters from boat center

# Sail configurations
sails:
  - name: "sail_name"
    datasheet: "data/sail_data.cvs"
    material_density: 1.204           # air density
    wetted_area: 10.0                 # sail area in m²
    rotational_inertia: 0
    size: 5.0                         # boom length
    position:
      angle: 0
      distance: 0
    initial_angle: 45                 # initial sail trim
    
    # Winch configurations
    winches:
      - position:
          angle: 90
          distance: 0.5
        offset_angle: 0
        offset_distance: 0
        length: 10                    # sheet length
        radius: 0.05                  # winch radius

# Boat properties
boat:
  mass: 100  # kg

# Polar diagram settings
polars:
  recalculate: false  # Set to true to regenerate
  filename: "MyPolar"
```

## Hull Types

### Available Datasheets

- `naca0009-R0.69e6-F180.csv` - Low drag foil
- `naca0012(Re380000).csv` - Medium foil
- `naca0015-R7e7-F180.csv` - Common rudder/keel foil
- `xf-naca001034-il-1000000-Ex.csv` - High performance hull

### Hull Examples

**Main Hull:**
```yaml
- name: "main_hull"
  datasheet: "data/naca0015-R7e7-F180.csv"
  material_density: 1000  # water
  wetted_area: 0.5
  rotational_inertia: 2.0
  size: 2.0
  position:
    angle: 0
    distance: 0
```

**Rudder:**
```yaml
- name: "rudder"
  datasheet: "data/naca0015-R7e7-F180.csv"
  material_density: 1000
  wetted_area: 0.1
  rotational_inertia: 0.05
  size: 0.3
  position:
    angle: 180      # Behind the boat
    distance: 1.0   # Half hull length
```

**Outrigger (Ama):**
```yaml
- name: "port_ama"
  datasheet: "data/naca0009-R0.69e6-F180.csv"
  material_density: 997.77
  wetted_area: 0.2
  rotational_inertia: 1.0
  size: 1.5
  position:
    angle: 90       # Port side
    distance: 2.0   # 2 meters out
```

## Sail Types

### Available Sail Data

- `mainSailCoeffs.cvs` - Standard mainsail
- `MarchajSail.cvs` - Performance sail
- `wikiSailCoeffs.cvs` - Generic sail coefficients
- `combinedSailCoeffs.cvs` - Multi-sail coefficients

### Sail Examples

**Simple Mainsail:**
```yaml
- name: "mainsail"
  datasheet: "data/mainSailCoeffs.cvs"
  material_density: 1.204  # air
  wetted_area: 15.0       # 15 m² sail
  rotational_inertia: 0
  size: 5.0               # 5m boom
  position:
    angle: 0
    distance: 0
  initial_angle: 45
```

## Common Configurations

### Single Hull Dinghy
- 1 main hull
- 1 rudder
- 1 mainsail
- Simple and responsive

### Catamaran
- 2 main hulls (port and starboard)
- 1 or 2 rudders
- 1 large mainsail
- Stable and fast

### Trimaran with Outriggers
- 1 main hull (vaka)
- 2 outriggers (amas)
- 1 rudder
- 1 mainsail
- Very stable

## Tips

1. **Positions**: Use angle and distance to place components:
   - 0° = Forward
   - 90° = Port (left)
   - 180° = Aft (back)
   - -90° or 270° = Starboard (right)

2. **Material Density**:
   - Water: ~1000 kg/m³
   - Air: ~1.204 kg/m³

3. **Wetted Area**:
   - Hulls: Area in contact with water
   - Sails: Total sail area

4. **Size**:
   - Hulls: Length in meters
   - Sails: Boom length
   - Rudders: Chord length

5. **Testing**: Start with existing configs and modify gradually

## Command Line Usage

```bash
# Use default boat_config.yaml
python3 run_simulator.py

# Use custom configuration
python3 run_simulator.py --config my_boat.yaml

# Recalculate polars
python3 run_simulator.py --recalc-polars
```