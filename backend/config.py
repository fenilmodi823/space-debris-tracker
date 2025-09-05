# config.py
# Global configuration for the Space Debris Tracker project

# ============================================================
# 📡 TLE Fetching Configuration
# ============================================================
TLE_SOURCE_URL = "https://celestrak.org/NORAD/elements/gp.php"
TLE_DEFAULT_GROUP = "last-30-days"     # broader set for ML + viz (instead of "active")
TLE_FORMAT = "tle"
TLE_SAVE_PATH = "data/latest_tle.txt"

# For dataset building (ML training)
TLE_GROUPS_FOR_DATASET = [
    "last-30-days",          # broad mix
    "cosmos-2251-debris",    # debris cloud
    "iridium-33-debris",     # debris cloud
    # add more groups if needed
]

# ============================================================
# 🤖 Machine Learning Configuration
# ============================================================
DATASET_LABELED_PATH = "data/tle_features_labeled.csv"
DATASET_ALL_PATH = "data/tle_features_all.csv"
MODEL_DIR = "ml_models"
MODEL_PATH = f"{MODEL_DIR}/object_classifier.joblib"

# ============================================================
# 🛰 SPICE Toolkit Configuration (future feature)
# ============================================================
SPICE_KERNELS_PATH = "../kernels/"   # Update if using SPICE ephemeris data

# ============================================================
# 🖥 Visualization Parameters
# ============================================================
EARTH_RADIUS_KM = 6371.0             # For PyVista and Cartopy
MAX_SATELLITES_DISPLAYED = 50        # global cap for plots
MAX_SATS_2D_ANIM = 10                # subset limit for 2D animation
USE_ML_COLORS = True                 # color-code by ML prediction if available

# ============================================================
# 🧪 Simulation Defaults
# ============================================================
DEFAULT_TIME_WINDOW_MIN = 60         # Collision check window in minutes
DEFAULT_STEP_SECONDS = 30            # Time resolution for orbit prediction
COLLISION_THRESHOLD_KM = 10          # Danger threshold in km

# ============================================================
# 🧭 Runtime Settings
# ============================================================
VERBOSE_MODE = True                  # Enable detailed terminal output
