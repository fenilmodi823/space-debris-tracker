# config.py
# Global configuration for the Space Debris Tracker project

# ----------------------------
# 📡 TLE Fetching Configuration
# ----------------------------
TLE_SOURCE_URL = "https://celestrak.com/NORAD/elements/gp.php"
TLE_DEFAULT_GROUP = "active"         # e.g., "gps-ops", "stations", "iridium", etc.
TLE_FORMAT = "tle"
TLE_SAVE_PATH = "data/latest_tle.txt"

# ----------------------------
# 🛰 SPICE Toolkit Configuration
# ----------------------------
SPICE_KERNELS_PATH = "../kernels/"   # Update if using SPICE ephemeris data (future feature)

# ----------------------------
# 🖥 Visualization Parameters (optional)
# ----------------------------
EARTH_RADIUS_KM = 6371.0             # For PyVista and Cartopy
MAX_SATELLITES_DISPLAYED = 50        # Performance tuning for orbit renderers

# ----------------------------
# 🧪 Simulation Defaults
# ----------------------------
DEFAULT_TIME_WINDOW_MIN = 60         # Collision check window in minutes
DEFAULT_STEP_SECONDS = 30            # Time resolution for orbit prediction
COLLISION_THRESHOLD_KM = 10          # Danger threshold in km

# ----------------------------
# 🧭 Runtime Settings
# ----------------------------
VERBOSE_MODE = True                 # Enable detailed terminal output
