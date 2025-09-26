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

# --- Added: NASA/CelesTrak configuration (Hybrid Approach: Step 1) ---
import os
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv optional; code still runs, but .env won't be loaded automatically
    pass

NASA_API_KEY = os.getenv("NASA_API_KEY") or "DEMO_KEY"

CELESTRAK_TLE_URL = os.getenv(
    "CELESTRAK_TLE_URL",
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle",
)
DONKI_BASE = os.getenv("DONKI_BASE", "https://api.nasa.gov/DONKI")
NEO_BASE   = os.getenv("NEO_BASE",   "https://api.nasa.gov/neo/rest/v1")

def get_config_summary() -> str:
    key_label = "DEMO_KEY" if NASA_API_KEY == "DEMO_KEY" else "SET (hidden)"
    return (
        "[Config]\n"
        f"  NASA_API_KEY: {key_label}\n"
        f"  CELESTRAK_TLE_URL: {CELESTRAK_TLE_URL}\n"
        f"  DONKI_BASE: {DONKI_BASE}\n"
        f"  NEO_BASE: {NEO_BASE}\n"
    )
# --- End added section ---
