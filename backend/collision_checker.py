from skyfield.api import load
from itertools import combinations
import numpy as np
from utils import calculate_distance_km

# ----------------------------------
# Collision Detection
# ----------------------------------

def check_collisions(satellites, threshold_km=10, minutes=60, step_seconds=30, verbose=True):
    """
    Checks for potential collisions between all satellite pairs.

    Parameters:
        satellites (list): List of Skyfield EarthSatellite objects.
        threshold_km (float): Distance threshold (in km) for collision alert.
        minutes (int): Time window to simulate ahead.
        step_seconds (int): Simulation resolution in seconds.
        verbose (bool): Whether to print per-step debug info.

    Prints:
        Collision alerts showing satellite names, closest approach distance, and timestamp.
    """
    ts = load.timescale()
    t0 = ts.now()
    step_days = step_seconds / 86400

    time_steps = [
        t0 + i * step_days
        for i in range((minutes * 60) // step_seconds)
    ]

    if verbose:
        print(f"Checking {len(satellites)} satellites over {minutes} minutes at {step_seconds}s resolution...")

    # Precompute satellite positions
    sat_positions = []
    for sat in satellites:
        try:
            track = [np.array(sat.at(t).position.km) for t in time_steps]
            sat_positions.append((sat.name, track))
        except Exception as e:
            if verbose:
                print(f"Skipping {sat.name}: {e}")
            continue

    # Compare all unique pairs
    alerts = []
    for (name1, track1), (name2, track2) in combinations(sat_positions, 2):
        min_dist = float('inf')
        min_idx = -1

        for i, (pos1, pos2) in enumerate(zip(track1, track2)):
            dist = calculate_distance_km(pos1, pos2)
            if dist < min_dist:
                min_dist = dist
                min_idx = i

        if min_dist < threshold_km:
            alert_time = time_steps[min_idx].utc_strftime('%H:%M:%S')
            alert_msg = f"Close approach: {name1} ↔ {name2} — {min_dist:.2f} km at {alert_time}"
            print(alert_msg)
            alerts.append(alert_msg)

    if not alerts:
        print("No close approaches detected within the threshold.")

    return alerts
