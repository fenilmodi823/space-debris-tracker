# backend/__init__.py
"""
Backend package for Space Debris Tracker.
Provides access to core submodules without side effects on import.
"""

__version__ = "0.1.0"

from . import config
from . import tle_fetcher
from . import orbit_predictor
from . import collision_checker
from . import visualizer
from . import orbit_plotter

__all__ = [
    "config",
    "tle_fetcher",
    "orbit_predictor",
    "collision_checker",
    "visualizer",
    "orbit_plotter",
]
