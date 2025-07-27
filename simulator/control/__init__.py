"""Control system components."""

from .ControlModular import ModularController
from .Control import Controler  # Original controller for backward compatibility

# Import modular controllers
from .controllers import (
    BaseRudderController, BaseSailController, BasePathfindingController,
    SimpleRudderController, WaypointRudderController,
    SimpleSailController, PolarBasedSailController,
    SimplePathfindingController
)

__all__ = [
    'ModularController', 'Controler',
    'BaseRudderController', 'BaseSailController', 'BasePathfindingController',
    'SimpleRudderController', 'WaypointRudderController', 
    'SimpleSailController', 'PolarBasedSailController',
    'SimplePathfindingController'
]