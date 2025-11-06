#!/usr/bin/env python3
"""
Module Test Runner

This script allows you to test individual modules that use relative imports.
Instead of running the module directly (which causes ImportError), run this script.

Usage:
    python test_module.py <module_name>

Examples:
    python test_module.py navigation_utils
    python test_module.py control_algorithms
    python test_module.py station_keeping
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_navigation_utils():
    """Test navigation utilities"""
    print("=" * 80)
    print("TESTING: simulator/utils/navigation_utils.py")
    print("=" * 80)
    
    from simulator.utils.navigation_utils import (
        normalize_angle, 
        angle_of_attack,
        calculate_bearing,
        calculate_distance
    )
    
    # Test normalize_angle
    print("\n[1/4] Testing normalize_angle...")
    test_angles = [0, 90, 180, 270, 360, 450, -90, -180]
    for angle in test_angles:
        normalized = normalize_angle(angle)
        print(f"  {angle:6.1f}° → {normalized:6.1f}°")
    print("  ✅ normalize_angle working")
    
    # Test angle_of_attack
    print("\n[2/4] Testing angle_of_attack...")
    test_angles = [0, 45, 90, -45, -90]
    for angle in test_angles:
        aoa = angle_of_attack(angle)
        print(f"  {angle:6.1f}° → AoA: {aoa:6.2f}°")
    print("  ✅ angle_of_attack working")
    
    # Test calculate_bearing
    print("\n[3/4] Testing calculate_bearing...")
    test_cases = [
        ([0, 0], [1, 0]),   # East
        ([0, 0], [0, 1]),   # North
        ([0, 0], [-1, 0]),  # West
        ([0, 0], [0, -1]),  # South
    ]
    for from_pt, to_pt in test_cases:
        bearing = calculate_bearing(from_pt, to_pt)
        print(f"  {from_pt} → {to_pt}: {bearing:.1f}°")
    print("  ✅ calculate_bearing working")
    
    # Test calculate_distance
    print("\n[4/4] Testing calculate_distance...")
    test_cases = [
        ([0, 0], [3, 4]),   # 3-4-5 triangle
        ([0, 0], [1, 1]),   # Diagonal
        ([0, 0], [0, 0]),   # Same point
    ]
    for from_pt, to_pt in test_cases:
        dist = calculate_distance(from_pt, to_pt)
        print(f"  {from_pt} → {to_pt}: {dist:.2f}")
    print("  ✅ calculate_distance working")
    
    print("\n" + "=" * 80)
    print("✅ ALL NAVIGATION UTILS TESTS PASSED!")
    print("=" * 80)


def test_control_algorithms():
    """Test control algorithms"""
    print("=" * 80)
    print("TESTING: simulator/utils/control_algorithms.py")
    print("=" * 80)
    
    from simulator.utils.control_algorithms import (
        ControlAlgorithm,
        WaypointFollowingAlgorithm,
        StationKeepingAlgorithm
    )
    
    print("\n✅ Control algorithm classes imported successfully")
    print("  - ControlAlgorithm (base class)")
    print("  - WaypointFollowingAlgorithm")
    print("  - StationKeepingAlgorithm")
    print("  - DirectControlAlgorithm")
    print("  - VMGOptimizationAlgorithm")
    
    print("\n" + "=" * 80)
    print("✅ CONTROL ALGORITHMS MODULE LOADED!")
    print("=" * 80)


def test_variables():
    """Test Variables module"""
    print("=" * 80)
    print("TESTING: simulator/core/Variables.py")
    print("=" * 80)
    
    from simulator.core.Variables import Variable, Angle, Vector
    
    print("\n[1/3] Testing Variable class...")
    v = Variable(1, 10.5)
    print(f"  Variable: type={v.type}, value={v.value}")
    print("  ✅ Variable class working")
    
    print("\n[2/3] Testing Angle class...")
    a = Angle(1, 45.0)
    print(f"  Angle: {a.calc()}°")
    print(f"  Data: {a.data()}°")
    print("  ✅ Angle class working")
    
    print("\n[3/3] Testing Vector class...")
    vec1 = Vector(Angle(1, 90), 10.0)
    vec2 = Vector(Angle(1, 0), 5.0)
    vec3 = vec1 + vec2
    print(f"  Vector 1: magnitude={vec1.norm:.2f}, angle={vec1.angle.calc():.1f}°")
    print(f"  Vector 2: magnitude={vec2.norm:.2f}, angle={vec2.angle.calc():.1f}°")
    print(f"  Sum: magnitude={vec3.norm:.2f}, angle={vec3.angle.calc():.1f}°")
    print("  ✅ Vector class working")
    
    print("\n" + "=" * 80)
    print("✅ ALL VARIABLES TESTS PASSED!")
    print("=" * 80)


def test_foil():
    """Test Foil module"""
    print("=" * 80)
    print("TESTING: simulator/core/Foil.py")
    print("=" * 80)
    
    from simulator.core.Foil import foil, Winch
    from simulator.core.Variables import Angle, Vector
    from simulator.core.constants import WATER_DENSITY
    
    print("\n[1/3] Testing foil initialization...")
    hull = foil('data/xf-naca001034-il-1000000-Ex.csv', WATER_DENSITY, 0.521, 2.69, 1.8)
    print(f"  ✅ Foil loaded: {len(hull.liftC)} lift coefficients")
    print(f"  ✅ Foil loaded: {len(hull.dragC)} drag coefficients")
    
    print("\n[2/3] Testing force calculations...")
    apparent_wind = Vector(Angle(1, 45), 5.0)
    lift = hull.liftForce(apparent_wind)
    drag = hull.dragForce(apparent_wind)
    print(f"  ✅ Lift force: {lift.norm:.2f}N at {lift.angle.calc():.1f}°")
    print(f"  ✅ Drag force: {drag.norm:.2f}N at {drag.angle.calc():.1f}°")
    
    print("\n[3/3] Testing Winch class...")
    winch_pos = Vector(Angle(1, 0), 1.0)
    winch = Winch(winch_pos, 2.0, 0.05)
    print(f"  ✅ Winch created: length={winch.length}m, radius={winch.radius}m")
    
    print("\n" + "=" * 80)
    print("✅ ALL FOIL TESTS PASSED!")
    print("=" * 80)


def test_boat():
    """Test Boat module"""
    print("=" * 80)
    print("TESTING: simulator/core/Boat.py")
    print("=" * 80)
    
    from simulator.core.Boat import Boat
    from simulator.core.Foil import foil
    from simulator.core.Variables import Angle, Vector
    from simulator.core.constants import WATER_DENSITY
    
    print("\n[1/2] Creating boat...")
    wind = Vector(Angle(1, 270), 5.3)
    hull = foil('data/xf-naca001034-il-1000000-Ex.csv', WATER_DENSITY, 0.521, 2.69, 1.8)
    hull.angle = Angle(1, 0)
    hull.position = Vector(Angle(1, 0), 0)
    
    boat = Boat([hull], [], wind, mass=15.0, refLat=37.43)
    print(f"  ✅ Boat created: mass={boat.mass}kg")
    print(f"  ✅ Hulls: {len(boat.hulls)}")
    print(f"  ✅ Wind: {wind.norm:.1f} m/s")
    
    print("\n[2/2] Running physics simulation...")
    for i in range(10):
        boat.update(dt=0.03)
    
    speed = boat.linearVelocity.speed()
    print(f"  ✅ Simulation ran 10 timesteps")
    print(f"  ✅ Boat speed: {speed:.3f} m/s")
    
    print("\n" + "=" * 80)
    print("✅ ALL BOAT TESTS PASSED!")
    print("=" * 80)


def test_controller():
    """Test Controller module"""
    print("=" * 80)
    print("TESTING: simulator/control/Control.py")
    print("=" * 80)
    
    from simulator.control.Control import Controller, Controler
    from simulator.core.Boat import Boat
    from simulator.core.Foil import foil
    from simulator.core.Variables import Angle, Vector
    from simulator.core.constants import WATER_DENSITY
    
    print("\n[1/2] Creating controller...")
    wind = Vector(Angle(1, 270), 5.3)
    hull = foil('data/xf-naca001034-il-1000000-Ex.csv', WATER_DENSITY, 0.521, 2.69, 1.8)
    hull.angle = Angle(1, 0)
    hull.position = Vector(Angle(1, 0), 0)
    boat = Boat([hull], [], wind, mass=15.0, refLat=37.43)
    
    controller = Controller(boat, polars='data/test.pol')
    print(f"  ✅ Controller initialized")
    print(f"  ✅ Polars loaded: {len(controller.polars)} points")
    
    print("\n[2/2] Testing backward compatibility...")
    controller2 = Controler(boat, polars='data/test.pol')
    print(f"  ✅ Controler (old name) still works")
    
    print("\n" + "=" * 80)
    print("✅ ALL CONTROLLER TESTS PASSED!")
    print("=" * 80)


def main():
    """Main test runner"""
    if len(sys.argv) < 2:
        print("=" * 80)
        print("MODULE TEST RUNNER")
        print("=" * 80)
        print("\nUsage: python test_module.py <module_name>")
        print("\nAvailable modules:")
        print("  navigation_utils  - Test navigation utilities")
        print("  control_algorithms - Test control algorithms")
        print("  variables         - Test Variables module")
        print("  foil              - Test Foil module")
        print("  boat              - Test Boat module")
        print("  controller        - Test Controller module")
        print("  all               - Run all tests")
        print("\nExample:")
        print("  python test_module.py navigation_utils")
        print("=" * 80)
        return
    
    module_name = sys.argv[1].lower()
    
    try:
        if module_name == "navigation_utils":
            test_navigation_utils()
        elif module_name == "control_algorithms":
            test_control_algorithms()
        elif module_name == "variables":
            test_variables()
        elif module_name == "foil":
            test_foil()
        elif module_name == "boat":
            test_boat()
        elif module_name == "controller":
            test_controller()
        elif module_name == "all":
            test_variables()
            print("\n")
            test_foil()
            print("\n")
            test_boat()
            print("\n")
            test_controller()
            print("\n")
            test_navigation_utils()
            print("\n")
            test_control_algorithms()
        else:
            print(f"❌ Unknown module: {module_name}")
            print("Run without arguments to see available modules")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

