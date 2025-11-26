from itertools import combinations
import numpy as np
from skyfield.api import load, EarthSatellite
from backend.utils import calculate_distance_km
from typing import List, Set, Optional, Tuple


# ----------------------------------
# Collision Detection
# ----------------------------------

def check_collisions(
    satellites: List[EarthSatellite],
    threshold_km: float = 10.0,
    minutes: int = 60,
    step_seconds: int = 30,
    verbose: bool = True,
    include_types: Optional[Set[str]] = None,      # e.g., {"Debris", "Rocket Body"}
    min_confidence: float = 0.0       # ignore sats with pred_conf < this
) -> List[str]:
    """
    Checks for potential close approaches between satellite pairs.
    
    This performs a pairwise check (O(N^2)) over a time grid.
    For large N, this can be slow. Consider using spatial indexing (KDTree)
    or SGP4 propagators with filters for production use.

    Parameters:
        satellites: List of Skyfield EarthSatellite objects to analyze.
        threshold_km: Distance threshold (km) for triggering an alert.
        minutes: Look-ahead time window in minutes.
        step_seconds: Simulation step size in seconds.
        verbose: If True, prints progress and skipped satellites.
        include_types: Optional set of strings. If provided, only satellites whose
            `pred_type` attribute is in this set are considered.
        min_confidence: If `pred_conf` attribute exists and is below this value,
            the satellite is skipped.

    Returns:
        List of human-readable alert strings describing close approaches.
    """
    ts = load.timescale()
    t0 = ts.now()
    step_days = step_seconds / 86400.0

    n_steps = max(1, (minutes * 60) // step_seconds)
    time_steps = [t0 + i * step_days for i in range(n_steps)]

    # Optional ML-based filtering
    def _ml_ok(sat: EarthSatellite) -> bool:
        if include_types:
            sat_type = getattr(sat, "pred_type", None)
            if sat_type not in include_types:
                return False
        if min_confidence > 0.0:
            conf = float(getattr(sat, "pred_conf", 1.0))
            if conf < min_confidence:
                return False
        return True

    # Build usable satellites and precompute tracks
    usable: List[Tuple[EarthSatellite, List[np.ndarray]]] = []
    for sat in satellites:
        if not _ml_ok(sat):
            if verbose:
                name = getattr(sat, "name", "UNKNOWN")
                print(f"[skip] {name}: filtered by ML (type/conf)")
            continue

        try:
            # Pre-calculate position vectors for all time steps
            # .position.km returns [x, y, z] in GCRS
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
        
        # Vectorized distance check would be faster, but keeping it simple/readable
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
