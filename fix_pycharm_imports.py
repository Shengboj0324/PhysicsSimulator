#!/usr/bin/env python3
"""
Fix PyCharm Import Errors

This script fixes PyCharm's import resolution by:
1. Ensuring all __init__.py files exist
2. Creating a proper .pth file for the project
3. Verifying all imports work correctly
4. Providing instructions for PyCharm configuration

Run this script to fix all import errors in PyCharm.
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"   {text}")


def check_init_files():
    """Check and create missing __init__.py files"""
    print_header("STEP 1: Checking __init__.py Files")
    
    project_root = Path(__file__).parent
    simulator_dir = project_root / "simulator"
    
    # Find all Python package directories
    package_dirs = []
    for root, dirs, files in os.walk(simulator_dir):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        # Check if directory contains Python files
        has_py_files = any(f.endswith('.py') for f in files)
        if has_py_files:
            package_dirs.append(Path(root))
    
    missing_init = []
    existing_init = []
    
    for pkg_dir in package_dirs:
        init_file = pkg_dir / "__init__.py"
        if not init_file.exists():
            missing_init.append(pkg_dir)
            # Create the __init__.py file
            init_file.write_text(f'"""Package: {pkg_dir.name}"""\n')
            print_success(f"Created: {init_file.relative_to(project_root)}")
        else:
            existing_init.append(pkg_dir)
            print_info(f"Exists: {init_file.relative_to(project_root)}")
    
    print(f"\n{GREEN}Summary:{RESET}")
    print(f"  Existing __init__.py files: {len(existing_init)}")
    print(f"  Created __init__.py files: {len(missing_init)}")
    
    return len(missing_init) == 0


def verify_imports():
    """Verify that all imports work correctly"""
    print_header("STEP 2: Verifying Imports")
    
    test_imports = [
        ("simulator.core.Variables", "Angle, Vector"),
        ("simulator.core.Boat", "Boat"),
        ("simulator.core.Foil", "foil, Winch"),
        ("simulator.core.exceptions", "SimulatorError, ValidationError"),
        ("simulator.core.logger", "logger"),
        ("simulator.core.validators", "Validator"),
        ("simulator.core.config", "get_config"),
        ("simulator.core.constants", "WATER_DENSITY, AIR_DENSITY"),
        ("simulator.control.Control", "Controller"),
        ("simulator.control.ControlModular", "ModularController"),
        ("simulator.utils.navigation_utils", "normalize_angle"),
        ("simulator.utils.control_algorithms", "ControlAlgorithm"),
    ]
    
    all_passed = True
    
    for module_name, imports in test_imports:
        try:
            exec(f"from {module_name} import {imports}")
            print_success(f"{module_name}")
        except Exception as e:
            print_error(f"{module_name}: {e}")
            all_passed = False
    
    return all_passed


def create_pth_file():
    """Create a .pth file for the project"""
    print_header("STEP 3: Creating .pth File")
    
    project_root = Path(__file__).parent.absolute()
    
    # Find site-packages directory in virtual environment
    venv_dir = project_root / ".venv"
    
    if not venv_dir.exists():
        print_warning(".venv directory not found")
        return False
    
    # Find site-packages
    site_packages = None
    for root, dirs, files in os.walk(venv_dir):
        if 'site-packages' in root:
            site_packages = Path(root)
            break
    
    if not site_packages:
        print_warning("site-packages directory not found in .venv")
        return False
    
    # Create .pth file
    pth_file = site_packages / "physics_simulator.pth"
    pth_file.write_text(str(project_root) + "\n")
    
    print_success(f"Created: {pth_file}")
    print_info(f"Added path: {project_root}")
    
    return True


def print_pycharm_instructions():
    """Print instructions for configuring PyCharm"""
    print_header("STEP 4: PyCharm Configuration Instructions")
    
    project_root = Path(__file__).parent.absolute()
    venv_python = project_root / ".venv" / "bin" / "python"
    
    print(f"{YELLOW}To fix import errors in PyCharm, follow these steps:{RESET}\n")
    
    print(f"{GREEN}1. Set Python Interpreter:{RESET}")
    print(f"   • Go to: PyCharm → Preferences → Project: PhysicsSimulator → Python Interpreter")
    print(f"   • Click the gear icon ⚙️ → Add...")
    print(f"   • Select 'Existing environment'")
    print(f"   • Set interpreter path to: {venv_python}")
    print(f"   • Click OK\n")
    
    print(f"{GREEN}2. Mark Directory as Sources Root:{RESET}")
    print(f"   • In Project view, right-click on 'PhysicsSimulator' (project root)")
    print(f"   • Select: Mark Directory as → Sources Root")
    print(f"   • The folder icon should turn blue\n")
    
    print(f"{GREEN}3. Invalidate Caches:{RESET}")
    print(f"   • Go to: File → Invalidate Caches / Restart...")
    print(f"   • Check 'Invalidate and Restart'")
    print(f"   • Click 'Invalidate and Restart'\n")
    
    print(f"{GREEN}4. Verify Configuration:{RESET}")
    print(f"   • Open any file in simulator/core/ (e.g., Foil.py)")
    print(f"   • Check that imports are no longer underlined in red")
    print(f"   • Hover over imports - they should resolve correctly\n")
    
    print(f"{YELLOW}Alternative: Use Terminal Instead of PyCharm Runner{RESET}")
    print(f"   • PyCharm's import errors are cosmetic - code runs fine")
    print(f"   • Use terminal: source .venv/bin/activate && python run_simulator.py")
    print(f"   • Or use: python test_module.py <module_name>\n")


def create_pycharm_config():
    """Create PyCharm configuration files"""
    print_header("STEP 5: Creating PyCharm Configuration Files")
    
    project_root = Path(__file__).parent
    idea_dir = project_root / ".idea"
    
    # Create .idea directory if it doesn't exist
    idea_dir.mkdir(exist_ok=True)
    
    # Create misc.xml with Python interpreter settings
    misc_xml = idea_dir / "misc.xml"
    misc_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.9 (PhysicsSimulator)" project-jdk-type="Python SDK" />
</project>
'''
    
    try:
        misc_xml.write_text(misc_content)
        print_success(f"Created: {misc_xml.relative_to(project_root)}")
    except Exception as e:
        print_warning(f"Could not create misc.xml: {e}")
    
    return True


def main():
    """Main function"""
    print_header("PyCharm Import Error Fix Tool")
    
    print(f"{BLUE}This tool will:{RESET}")
    print("  1. Check and create missing __init__.py files")
    print("  2. Verify all imports work correctly")
    print("  3. Create .pth file for the project")
    print("  4. Provide PyCharm configuration instructions")
    print("  5. Create PyCharm configuration files")
    
    # Step 1: Check __init__.py files
    init_ok = check_init_files()
    
    # Step 2: Verify imports
    imports_ok = verify_imports()
    
    # Step 3: Create .pth file
    pth_ok = create_pth_file()
    
    # Step 4: Print PyCharm instructions
    print_pycharm_instructions()
    
    # Step 5: Create PyCharm config
    config_ok = create_pycharm_config()
    
    # Final summary
    print_header("SUMMARY")
    
    if init_ok and imports_ok:
        print_success("All Python imports are working correctly!")
        print_success("The code will run without errors from terminal")
        print()
        print(f"{YELLOW}If you still see red underlines in PyCharm:{RESET}")
        print("  1. Follow the PyCharm configuration instructions above")
        print("  2. Restart PyCharm after making changes")
        print("  3. The errors are cosmetic - code runs fine in terminal")
        print()
        print(f"{GREEN}Quick Test:{RESET}")
        print("  source .venv/bin/activate")
        print("  python test_module.py all")
        print()
    else:
        print_error("Some imports failed - please check the errors above")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

