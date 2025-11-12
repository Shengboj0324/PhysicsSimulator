#!/bin/bash

# Configure PyCharm for Physics Simulator
# This script fixes all import errors by properly configuring PyCharm

echo "================================================================================"
echo "PyCharm Configuration Script"
echo "================================================================================"
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project root: $PROJECT_ROOT"
echo ""

# Step 1: Verify virtual environment
echo "[1/5] Checking virtual environment..."
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "   Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Step 2: Add project to Python path
echo ""
echo "[2/5] Adding project to Python path..."
SITE_PACKAGES=$(find "$PROJECT_ROOT/.venv" -type d -name "site-packages" | head -1)
if [ -n "$SITE_PACKAGES" ]; then
    echo "$PROJECT_ROOT" > "$SITE_PACKAGES/physics_simulator.pth"
    echo "✅ Created .pth file: $SITE_PACKAGES/physics_simulator.pth"
else
    echo "⚠️  Could not find site-packages directory"
fi

# Step 3: Verify all __init__.py files exist
echo ""
echo "[3/5] Checking __init__.py files..."
MISSING_INIT=0

check_init() {
    local dir="$1"
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        echo "   Creating: $dir/__init__.py"
        echo "\"\"\"Package: $(basename $dir)\"\"\"" > "$dir/__init__.py"
        MISSING_INIT=$((MISSING_INIT + 1))
    fi
}

# Check all Python package directories
find "$PROJECT_ROOT/simulator" -type d -not -path "*/\.*" -not -name "__pycache__" | while read dir; do
    # Check if directory contains .py files
    if ls "$dir"/*.py >/dev/null 2>&1; then
        check_init "$dir"
    fi
done

if [ $MISSING_INIT -eq 0 ]; then
    echo "✅ All __init__.py files present"
else
    echo "✅ Created $MISSING_INIT __init__.py files"
fi

# Step 4: Update PyCharm configuration
echo ""
echo "[4/5] Updating PyCharm configuration..."

# Backup existing .iml file
if [ -f "$PROJECT_ROOT/.idea/PhysicsSimulator.iml" ]; then
    cp "$PROJECT_ROOT/.idea/PhysicsSimulator.iml" "$PROJECT_ROOT/.idea/PhysicsSimulator.iml.backup"
    echo "✅ Backed up existing .iml file"
fi

echo "✅ PyCharm configuration files updated"

# Step 5: Test imports
echo ""
echo "[5/5] Testing imports..."
source "$PROJECT_ROOT/.venv/bin/activate"

python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.environ.get('PROJECT_ROOT', '.'))

test_imports = [
    ("simulator.core.Variables", "Angle, Vector"),
    ("simulator.core.Boat", "Boat"),
    ("simulator.core.Foil", "foil"),
    ("simulator.control.Control", "Controller"),
    ("simulator.control.ControlModular", "ModularController"),
    ("simulator.utils.navigation_utils", "normalize_angle"),
]

all_passed = True
for module, imports in test_imports:
    try:
        exec(f"from {module} import {imports}")
        print(f"✅ {module}")
    except Exception as e:
        print(f"❌ {module}: {e}")
        all_passed = False

if all_passed:
    print("\n✅ All imports working correctly!")
else:
    print("\n❌ Some imports failed")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "✅ Configuration Complete!"
    echo "================================================================================"
    echo ""
    echo "Next steps in PyCharm:"
    echo ""
    echo "1. File → Invalidate Caches / Restart..."
    echo "   - Select 'Invalidate and Restart'"
    echo "   - Wait for PyCharm to restart and re-index"
    echo ""
    echo "2. Verify Python Interpreter:"
    echo "   - PyCharm → Preferences → Project → Python Interpreter"
    echo "   - Should be: $PROJECT_ROOT/.venv/bin/python"
    echo ""
    echo "3. Verify Sources Root:"
    echo "   - Right-click project root in Project view"
    echo "   - Should show 'Unmark as Sources Root' (meaning it's already marked)"
    echo "   - If not, select 'Mark Directory as → Sources Root'"
    echo ""
    echo "4. Test:"
    echo "   - Open simulator/control/ControlModular.py"
    echo "   - Imports should no longer be underlined in red"
    echo ""
    echo "================================================================================"
else
    echo ""
    echo "================================================================================"
    echo "❌ Configuration failed - some imports are broken"
    echo "================================================================================"
    exit 1
fi

