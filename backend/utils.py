# utils.py
# Reusable helper functions for the Space Debris Tracker

import numpy as np
from datetime import datetime

# ----------------------------------
# Distance & Vector Calculations
# ----------------------------------

def calculate_distance_km(pos1, pos2):
    """
    Returns the Euclidean distance in kilometers between two 3D positions.
    """
    return np.linalg.norm(np.array(pos1) - np.array(pos2))


def estimate_velocity_kms(pos1, pos2, delta_seconds=1):
    """
    Estimates velocity (in km/s) between two position vectors spaced by delta_seconds.
    """
    return calculate_distance_km(pos1, pos2) / delta_seconds

# ----------------------------------
# Time Formatting
# ----------------------------------

def get_utc_timestamp():
    """
    Returns current UTC timestamp in readable string format.
    """
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

# ----------------------------------
# Satellite Visualization
# ----------------------------------

FAMOUS_SAT_COLORS = {
    "ISS (ZARYA)": "white",
    "HUBBLE SPACE TELESCOPE": "violet",
    "LANDSAT 8": "green",
    "SENTINEL-2A": "cyan",
    "STARLINK-30000": "blue"
}

def get_satellite_color(name, fallback='red'):
    """
    Returns a preset color for well-known satellites, or fallback color if not matched.
    """
    return FAMOUS_SAT_COLORS.get(name.upper(), fallback)

def is_famous_satellite(name):
    """
    Returns True if satellite is in the famous satellite list.
    """
    return name.upper() in FAMOUS_SAT_COLORS
