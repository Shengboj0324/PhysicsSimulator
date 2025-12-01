"""
Simulator Configuration File - Industrial Grade

To use a custom control algorithm:
1. Create your algorithm in the algorithms/ directory
2. Import it here
3. Set CONTROL_ALGORITHM to your algorithm class
4. Run: python run_simulator.py

Enhanced with:
- Absolute imports with fallback
- Error handling
- Logging
"""

import sys

# Fix imports - use absolute imports with fallback
try:
    from simulator.control.algorithms.example_zigzag import ZigzagAlgorithm
except ImportError:
    try:
        from ..control.algorithms.example_zigzag import ZigzagAlgorithm
    except ImportError:
        # Fallback if algorithm not available
        ZigzagAlgorithm = None
        print("WARNING: ZigzagAlgorithm not available, using default algorithms")

# ============================================
# SELECT YOUR CONTROL ALGORITHM
# ============================================

# Option 1: Use default algorithms (waypoint following, station keeping)
# CONTROL_ALGORITHM = None
CONTROL_ALGORITHM = ZigzagAlgorithm

# Option 2: Use an example algorithm
# from ..control.algorithms.beam_reach_algorithm import BeamReachAlgorithm
# CONTROL_ALGORITHM = BeamReachAlgorithm

# Option 3: Use your custom algorithm
# from ..control.algorithms.my_algorithm import MyAlgorithm
# CONTROL_ALGORITHM = MyAlgorithm

# ============================================
# EXAMPLES (uncomment one to try)
# ============================================

# Example 1: Beam reach (fastest point of sail)
# from ..control.algorithms.beam_reach_algorithm import BeamReachAlgorithm
# CONTROL_ALGORITHM = BeamReachAlgorithm

# Example 2: Close hauled (sailing upwind)
# from ..control.algorithms.close_hauled_algorithm import CloseHauledAlgorithm
# CONTROL_ALGORITHM = CloseHauledAlgorithm

# Example 3: Compass heading (maintain specific heading)
# from ..control.algorithms.compass_heading_algorithm import CompassHeadingAlgorithm
# CONTROL_ALGORITHM = CompassHeadingAlgorithm
