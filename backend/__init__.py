# backend/__init__.py

# Expose key modules
from . import tle_fetcher
from . import orbit_predictor
from . import collision_checker
from . import visualizer
from . import orbit_plotter

# Optional: Show setup message
print("Space Debris Tracker backend package loaded.")
