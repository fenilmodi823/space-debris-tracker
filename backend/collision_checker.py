from itertools import combinations
import numpy as np
from skyfield.api import load
from backend.utils import calculate_distance_km


# ----------------------------------
# Collision Detection
# ----------------------------------

def check_collisions(
    satellites,
    threshold_km=10,
    minutes=60,
    step_seconds=30,
    verbose=True,
    include_types=None,      # e.g., {"Debris", "Rocket Body"}
    min_confidence=0.0       # ignore sats with pred_conf < this
):
    """
    Checks for potential close approaches between satellite pairs.

    Parameters:
        satellites (list[EarthSatellite]): satellites to analyze
        threshold_km (float): distance threshold (km) for an alert
        minutes (int): look-ahead time window
        step_seconds (int): simulation step in seconds
        verbose (bool): print progress and skips
        include_types (set/list/None): if provided, only satellites whose
            sat.pred_type is in this collection are considered
        min_confidence (float): if sat.pred_conf exists and is below this,
            the satellite is skipped

    Returns:
        list[str]: human-readable alert messages
    """
    ts = load.timescale()
    t0 = ts.now()
    step_days = step_seconds / 86400.0

    n_steps = max(1, (minutes * 60) // step_seconds)
    time_steps = [t0 + i * step_days for i in range(n_steps)]

    # Optional ML-based filtering
    def _ml_ok(sat):
        if include_types:
            sat_type = getattr(sat, "pred_type", None)
            if sat_type not in set(include_types):
                return False
        if min_confidence > 0.0:
            conf = float(getattr(sat, "pred_conf", 1.0))
            if conf < min_confidence:
                return False
        return True

    # Build usable satellites and precompute tracks
    usable = []
    for sat in satellites:
        if not _ml_ok(sat):
            if verbose:
                name = getattr(sat, "name", "UNKNOWN")
                print(f"[skip] {name}: filtered by ML (type/conf)")
            continue

        try:
            track = [np.array(sat.at(t).position.km) for t in time_steps]
            usable.append((sat, track))
        except Exception as e:
            if verbose:
                print(f"[skip] {getattr(sat, 'name', 'UNKNOWN')}: {e}")
            continue

    if verbose:
        print(f"Checking {len(usable)} satellites over {minutes} minutes at {step_seconds}s resolution...")

    if len(usable) < 2:
        if verbose:
            print("Not enough satellites to compare.")
        return []

    # Compare all unique pairs
    alerts = []
    for (sat1, track1), (sat2, track2) in combinations(usable, 2):
        # Find minimum separation over the time grid
        dmin = float("inf")
        imin = -1
        for i, (p1, p2) in enumerate(zip(track1, track2)):
            d = calculate_distance_km(p1, p2)
            if d < dmin:
                dmin = d
                imin = i

        if dmin < threshold_km and imin >= 0:
            t_alert = time_steps[imin].utc_strftime("%H:%M:%S")

            # ML adornments (if present)
            t1 = getattr(sat1, "pred_type", None)
            c1 = getattr(sat1, "pred_conf", None)
            t2 = getattr(sat2, "pred_type", None)
            c2 = getattr(sat2, "pred_conf", None)

            def label(sat, t, c):
                base = getattr(sat, "name", "UNKNOWN")
                if t is not None and c is not None:
                    return f"{base} [{t} {c:.0%}]"
                if t is not None:
                    return f"{base} [{t}]"
                return base

            name1 = label(sat1, t1, c1)
            name2 = label(sat2, t2, c2)

            alert_msg = f"Close approach: {name1} ↔ {name2} — {dmin:.2f} km at {t_alert}"
            print(alert_msg)
            alerts.append(alert_msg)

    if not alerts:
        print("No close approaches detected within the threshold.")

    return alerts
