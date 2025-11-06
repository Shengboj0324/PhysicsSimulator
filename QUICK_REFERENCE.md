# Physics Sailing Simulator - Quick Reference Card

## 🚀 Getting Started

### **Activate Environment:**
```bash
source .venv/bin/activate
```

### **Run Simulator:**
```bash
python run_simulator.py
```

### **Test Modules:**
```bash
python test_module.py <module_name>
```

---

## 📦 Available Test Modules

| Command | Description |
|---------|-------------|
| `python test_module.py variables` | Test Variable, Angle, Vector classes |
| `python test_module.py foil` | Test Foil aerodynamics |
| `python test_module.py boat` | Test Boat physics engine |
| `python test_module.py controller` | Test Controller system |
| `python test_module.py navigation_utils` | Test navigation utilities |
| `python test_module.py control_algorithms` | Test control algorithms |
| `python test_module.py all` | Run all tests |

---

## 🔧 Common Tasks

### **Install/Update Packages:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### **View Logs:**
```bash
ls -la logs/
tail -f logs/simulator_*.log
```

### **Check Package Installation:**
```bash
source .venv/bin/activate
pip list
```

---

## 💻 Using the Simulator in Code

### **Import Core Classes:**
```python
from simulator.core.Variables import Angle, Vector, Variable
from simulator.core.Boat import Boat
from simulator.core.Foil import foil, Winch
from simulator.control.Control import Controller
from simulator.core.constants import WATER_DENSITY, AIR_DENSITY
from simulator.core.logger import logger
from simulator.core.validators import Validator
```

### **Create a Boat:**
```python
from simulator.core.Variables import Angle, Vector
from simulator.core.Boat import Boat
from simulator.core.Foil import foil
from simulator.core.constants import WATER_DENSITY

# Create wind
wind = Vector(Angle(1, 270), 5.3)  # 5.3 m/s from West

# Create hull
hull = foil('data/xf-naca001034-il-1000000-Ex.csv', 
            WATER_DENSITY, 0.521, 2.69, 1.8)
hull.angle = Angle(1, 0)
hull.position = Vector(Angle(1, 0), 0)

# Create boat
boat = Boat([hull], [], wind, mass=15.0, refLat=37.43)
```

### **Run Physics Simulation:**
```python
# Run for 1 second (30 timesteps)
for i in range(30):
    boat.update(dt=0.033)

# Check boat state
speed = boat.linearVelocity.speed()
heading = boat.angle.calc()
print(f"Speed: {speed:.2f} m/s, Heading: {heading:.1f}°")
```

### **Use Controller:**
```python
from simulator.control.Control import Controller

# Create controller
controller = Controller(boat, polars='data/test.pol')

# Plan waypoint course
waypoints = [
    [37.4275, -122.1697],
    [37.4280, -122.1690]
]
course = controller.plan('p', waypoints)

# Get control commands
rudder_angle = controller.rudder()
sail_angle = controller.sail()
```

### **Use Validation:**
```python
from simulator.core.validators import Validator

# Validate inputs
angle = Validator.validate_angle(45.0, "heading", min_val=0, max_val=360)
mass = Validator.validate_positive(15.0, "boat mass")

# Safe division
result = Validator.safe_divide(10, 0, default=99)  # Returns 99
```

### **Use Logging:**
```python
from simulator.core.logger import logger

logger.info("Starting simulation")
logger.debug(f"Boat position: {boat.position}")
logger.warning("Wind speed exceeds safe limits")
logger.error("Failed to load configuration", exc_info=True)
```

### **Use Constants:**
```python
from simulator.core.constants import (
    PI, DEG_TO_RAD, RAD_TO_DEG,
    WATER_DENSITY, AIR_DENSITY, GRAVITY,
    DEFAULT_RUDDER_MAX_ANGLE,
    MAX_REALISTIC_BOAT_SPEED
)

angle_rad = angle_deg * DEG_TO_RAD
density = WATER_DENSITY  # 997.77 kg/m³
```

---

## 📐 Coordinate Systems

### **Angle Types:**

| Type | Name | Range | Description |
|------|------|-------|-------------|
| 0 | DATA | 0-180° | For foil data lookup |
| 1 | CALC | 0-360° | Unit circle (0°=East, 90°=North) |
| 2 | DISPLAY | Any | Display with negatives allowed |

### **Creating Angles:**
```python
from simulator.core.Variables import Angle

angle_calc = Angle(1, 90)    # 90° in CALC system (North)
angle_data = Angle(0, 45)    # 45° in DATA system
angle_disp = Angle(2, -30)   # -30° in DISPLAY system

# Convert between systems
calc_value = angle_data.calc()
data_value = angle_calc.data()
disp_value = angle_calc.disp()
```

### **Creating Vectors:**
```python
from simulator.core.Variables import Angle, Vector

# Create vector: 10 m/s at 45°
vec = Vector(Angle(1, 45), 10.0)

# Vector operations
vec2 = Vector(Angle(1, 90), 5.0)
vec3 = vec + vec2  # Vector addition
vec4 = vec * 2.0   # Scalar multiplication

# Get components
x = vec.xcomp()
y = vec.ycomp()
magnitude = vec.norm
angle = vec.angle.calc()
```

---

## 🧪 Physics Formulas

### **Lift Force:**
```
F_lift = 0.5 × C_L × ρ × v² × A

Where:
  C_L = Lift coefficient (from foil data)
  ρ = Fluid density (water or air)
  v = Apparent velocity
  A = Foil area
```

### **Drag Force:**
```
F_drag = 0.5 × C_D × ρ × v² × A

Where:
  C_D = Drag coefficient (from foil data)
  ρ = Fluid density
  v = Apparent velocity
  A = Foil area
```

### **Apparent Wind:**
```
V_apparent = V_true - V_boat

Where:
  V_true = True wind vector
  V_boat = Boat velocity vector
```

---

## 🎯 Key Constants

| Constant | Value | Unit |
|----------|-------|------|
| `WATER_DENSITY` | 997.77 | kg/m³ |
| `AIR_DENSITY` | 1.204 | kg/m³ |
| `GRAVITY` | 9.80665 | m/s² |
| `PI` | 3.14159265359 | - |
| `DEG_TO_RAD` | 0.0174533 | rad/deg |
| `RAD_TO_DEG` | 57.2958 | deg/rad |
| `DEFAULT_RUDDER_MAX_ANGLE` | 45.0 | degrees |
| `MAX_REALISTIC_BOAT_SPEED` | 50.0 | m/s |
| `UPWIND_NO_GO_ANGLE` | 45.0 | degrees |
| `DOWNWIND_NO_GO_ANGLE` | 30.0 | degrees |

---

## 🐛 Troubleshooting

### **Import Error:**
```
ImportError: attempted relative import with no known parent package
```
**Solution:** Use `python test_module.py <module>` instead of running files directly.

### **Module Not Found:**
```
ModuleNotFoundError: No module named 'simulator'
```
**Solution:** Run from project root: `cd /Users/jiangshengbo/Desktop/PhysicsSimulator`

### **Virtual Environment Not Activated:**
```
ModuleNotFoundError: No module named 'numpy'
```
**Solution:** Activate environment: `source .venv/bin/activate`

### **File Not Found:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/...'
```
**Solution:** Make sure you're running from project root directory.

---

## 📁 Project Structure

```
PhysicsSimulator/
├── simulator/
│   ├── core/              # Core physics engine
│   │   ├── Variables.py   # Angle, Vector classes
│   │   ├── Boat.py        # Boat physics
│   │   ├── Foil.py        # Aerodynamics
│   │   ├── exceptions.py  # Custom exceptions
│   │   ├── logger.py      # Logging system
│   │   ├── validators.py  # Input validation
│   │   ├── config.py      # Configuration
│   │   └── constants.py   # Constants
│   ├── control/           # Control systems
│   │   ├── Control.py     # Main controller
│   │   └── ControlModular.py
│   ├── display/           # Visualization
│   └── utils/             # Utilities
│       ├── navigation_utils.py
│       └── control_algorithms.py
├── data/                  # Foil data, polars
├── logs/                  # Log files
├── .venv/                 # Virtual environment
├── run_simulator.py       # Main entry point
├── test_module.py         # Module test runner
└── boat_config.yaml       # Boat configuration
```

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `FINAL_UPGRADE_REPORT.md` | Complete upgrade documentation |
| `UPGRADE_SUMMARY.md` | Detailed upgrade summary |
| `HOW_TO_RUN_MODULES.md` | Guide to running modules |
| `IMPORT_ERRORS_FIXED.md` | Import error solutions |
| `QUICK_REFERENCE.md` | This file |

---

## ✅ Verification Checklist

Before running the simulator, verify:

- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] In project root: `pwd` shows `.../PhysicsSimulator`
- [ ] Packages installed: `pip list` shows numpy, pandas, etc.
- [ ] Data files exist: `ls data/` shows CSV files
- [ ] Config file exists: `ls boat_config.yaml`

---

## 🎓 Best Practices

### **DO:**
✅ Always activate virtual environment first  
✅ Run from project root directory  
✅ Use the test runner for module testing  
✅ Use logging instead of print statements  
✅ Validate all inputs with Validator class  
✅ Use constants instead of magic numbers  
✅ Handle exceptions properly  

### **DON'T:**
❌ Run module files directly  
❌ Modify package files manually  
❌ Use magic numbers in code  
❌ Ignore validation errors  
❌ Skip error handling  

---

## 🚀 Quick Start Example

```bash
# 1. Navigate to project
cd /Users/jiangshengbo/Desktop/PhysicsSimulator

# 2. Activate environment
source .venv/bin/activate

# 3. Test everything works
python test_module.py all

# 4. Run the simulator
python run_simulator.py
```

---

**Last Updated:** November 6, 2025  
**Version:** 2.0 (Industrial-Grade Upgrade)  
**Status:** ✅ Production-Ready

