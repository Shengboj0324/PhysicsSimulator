# How to Run Modules - Import Error Solutions

## 🚨 The Problem

When you try to run a Python module file directly that uses relative imports, you get this error:

```
ImportError: attempted relative import with no known parent package
```

**Example:**
```bash
python simulator/utils/navigation_utils.py
# ❌ ERROR: ImportError: attempted relative import with no known parent package
```

This happens because files with relative imports (like `from ..core.Variables import Angle`) **cannot be run directly** - they must be imported as part of a package.

---

## ✅ The Solutions

### **Solution 1: Use the Test Module Runner (Recommended)**

I've created a test runner script that properly handles module imports:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run specific module tests
python test_module.py navigation_utils
python test_module.py control_algorithms
python test_module.py variables
python test_module.py foil
python test_module.py boat
python test_module.py controller

# Run all tests
python test_module.py all
```

**Available test modules:**
- `navigation_utils` - Navigation utilities (normalize_angle, calculate_bearing, etc.)
- `control_algorithms` - Control algorithm classes
- `variables` - Variable, Angle, Vector classes
- `foil` - Foil aerodynamic calculations
- `boat` - Boat physics engine
- `controller` - Controller and waypoint planning
- `all` - Run all tests

---

### **Solution 2: Use Python's Module Execution**

Run the module as a package module instead of a script:

```bash
# Instead of this (WRONG):
python simulator/utils/navigation_utils.py

# Do this (CORRECT):
python -m simulator.utils.navigation_utils
```

**Note:** This only works if the module has a `if __name__ == "__main__":` block.

---

### **Solution 3: Import in Python REPL or Script**

Use the Python interactive shell or create a script that imports the module:

```bash
# Start Python REPL
source .venv/bin/activate
python

# Then import the module
>>> from simulator.utils.navigation_utils import normalize_angle
>>> normalize_angle(270)
-90.0
```

Or create a script:

```python
# my_test.py
from simulator.utils.navigation_utils import normalize_angle, calculate_bearing

angle = normalize_angle(270)
print(f"Normalized: {angle}°")

bearing = calculate_bearing([0, 0], [1, 1])
print(f"Bearing: {bearing}°")
```

Then run:
```bash
python my_test.py
```

---

### **Solution 4: Run the Main Simulator**

The proper way to use the simulator is through the main entry point:

```bash
source .venv/bin/activate
python run_simulator.py
```

---

## 📚 Understanding Relative Imports

### **What are Relative Imports?**

Relative imports use dots to specify the location relative to the current module:

```python
from ..core.Variables import Angle, Vector  # Go up one level, then into core
from .navigation_utils import normalize_angle  # Same directory
from ...utils import something  # Go up two levels
```

### **Why Can't You Run Them Directly?**

Python needs to know the package structure to resolve relative imports. When you run a file directly with `python file.py`, Python doesn't know it's part of a package, so relative imports fail.

### **The Fix:**

Either:
1. Run as a module: `python -m package.module`
2. Import from another script that's run from the project root
3. Use the test runner I created

---

## 🎯 Quick Reference

### **Testing Individual Modules:**

```bash
# Activate environment
source .venv/bin/activate

# Test navigation utilities
python test_module.py navigation_utils

# Test control algorithms
python test_module.py control_algorithms

# Test all modules
python test_module.py all
```

### **Running the Full Simulator:**

```bash
source .venv/bin/activate
python run_simulator.py
```

### **Using Modules in Your Code:**

```python
# my_script.py (in project root)
from simulator.core.Variables import Angle, Vector
from simulator.core.Boat import Boat
from simulator.control.Control import Controller
from simulator.utils.navigation_utils import normalize_angle

# Your code here
angle = normalize_angle(270)
print(f"Normalized angle: {angle}°")
```

Then run:
```bash
python my_script.py
```

---

## 🔧 PyCharm Configuration

If you're using PyCharm, you can configure it to run modules correctly:

### **Method 1: Run Configuration**

1. Right-click on the file you want to run
2. Select "Modify Run Configuration..."
3. Change "Script path" to "Module name"
4. Enter the module name (e.g., `simulator.utils.navigation_utils`)
5. Click OK

### **Method 2: Mark Directory as Sources Root**

1. Right-click on the project root directory
2. Select "Mark Directory as" → "Sources Root"
3. This helps PyCharm understand the package structure

### **Method 3: Use the Test Runner**

1. Open `test_module.py`
2. Right-click and select "Run 'test_module'"
3. Or create a run configuration for it

---

## 📝 Examples

### **Example 1: Testing Navigation Utils**

```bash
$ python test_module.py navigation_utils

================================================================================
TESTING: simulator/utils/navigation_utils.py
================================================================================

[1/4] Testing normalize_angle...
     0.0° →    0.0°
    90.0° →   90.0°
   270.0° →  -90.0°
  ✅ normalize_angle working

[2/4] Testing angle_of_attack...
  ✅ angle_of_attack working

[3/4] Testing calculate_bearing...
  ✅ calculate_bearing working

[4/4] Testing calculate_distance...
  ✅ calculate_distance working

✅ ALL NAVIGATION UTILS TESTS PASSED!
```

### **Example 2: Using in Your Own Script**

```python
# my_sailing_test.py
from simulator.core.Variables import Angle, Vector
from simulator.core.Boat import Boat
from simulator.core.Foil import foil
from simulator.core.constants import WATER_DENSITY

# Create wind
wind = Vector(Angle(1, 270), 5.3)

# Create hull
hull = foil('data/xf-naca001034-il-1000000-Ex.csv', 
            WATER_DENSITY, 0.521, 2.69, 1.8)
hull.angle = Angle(1, 0)
hull.position = Vector(Angle(1, 0), 0)

# Create boat
boat = Boat([hull], [], wind, mass=15.0, refLat=37.43)

# Run simulation
for i in range(10):
    boat.update(dt=0.03)

print(f"Boat speed: {boat.linearVelocity.speed():.3f} m/s")
```

Run it:
```bash
python my_sailing_test.py
```

---

## 🎓 Best Practices

### **DO:**
✅ Use `python test_module.py <module>` to test individual modules  
✅ Use `python run_simulator.py` to run the full simulator  
✅ Import modules in your scripts from the project root  
✅ Use `python -m package.module` for module execution  

### **DON'T:**
❌ Run module files directly with `python simulator/utils/file.py`  
❌ Try to run files with relative imports as scripts  
❌ Modify sys.path manually unless necessary  

---

## 🆘 Troubleshooting

### **Problem: "No module named 'simulator'"**

**Solution:** Make sure you're running from the project root directory:
```bash
cd /Users/jiangshengbo/Desktop/PhysicsSimulator
python test_module.py navigation_utils
```

### **Problem: "ImportError: attempted relative import"**

**Solution:** Don't run the file directly. Use one of the solutions above.

### **Problem: Virtual environment not activated**

**Solution:** Always activate the virtual environment first:
```bash
source .venv/bin/activate
```

### **Problem: Module not found in PyCharm**

**Solution:** 
1. Mark project root as "Sources Root"
2. Set Python interpreter to `.venv/bin/python`
3. Invalidate caches: File → Invalidate Caches / Restart

---

## 📖 Summary

**The key takeaway:** Python modules with relative imports cannot be run directly as scripts. Always use:

1. **Test runner:** `python test_module.py <module>`
2. **Module execution:** `python -m simulator.utils.module`
3. **Import in scripts:** Create a script that imports and uses the module
4. **Main entry point:** `python run_simulator.py`

This is standard Python behavior and applies to all properly structured Python packages!

---

**Created:** November 6, 2025  
**For:** Physics Sailing Simulator Project

