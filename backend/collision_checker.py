import numpy as np
from scipy.spatial import KDTree
from skyfield.api import load, EarthSatellite
from typing import List, Set, Optional


def check_collisions(
    satellites: List[EarthSatellite],
    threshold_km: float = 10.0,
    minutes: int = 60,
    step_seconds: int = 60,
    verbose: bool = True,
    include_types: Optional[Set[str]] = None,
    min_confidence: float = 0.0,
) -> List[str]:
    """
    Optimized collision detection using KD-Trees (Spatial Indexing).
    Complexity: O(T * N log N) instead of O(T * N^2).
    """
    ts = load.timescale()
    t0 = ts.now()
    step_days = step_seconds / 86400.0
    n_steps = max(1, (minutes * 60) // step_seconds)

    # Generate time steps
    times = [t0 + i * step_days for i in range(n_steps)]

    # Filter satellites first
    valid_sats = []
    for sat in satellites:
        # Check type filter
        if include_types:
            stype = getattr(sat, "pred_type", None)
            if stype not in include_types:
                continue
        # Check confidence filter
        if min_confidence > 0:
            conf = getattr(sat, "pred_conf", 1.0)
            if conf < min_confidence:
                continue
        valid_sats.append(sat)

    if len(valid_sats) < 2:
        return []

    if verbose:
        print(
            f"[⚡] Running KD-Tree collision check on {len(valid_sats)} satellites over {minutes} mins..."
        )

    alerts = set()  # Use set to avoid duplicate alerts

    # ---------------------------------------------------------
    # OPTIMIZATION: Evaluate positions in batches per time step
    # ---------------------------------------------------------
    for t_idx, t in enumerate(times):
        # 1. Bulk calculate positions for this timestep
        positions = []
        current_sats = []

        for sat in valid_sats:
            try:
                # Skyfield position calculation
                pos = sat.at(t).position.km
                positions.append(pos)
                current_sats.append(sat)
            except Exception:
                continue

        if len(positions) < 2:
            continue

        # 2. Build Spatial Index (KD-Tree)
        tree = KDTree(positions)

        # 3. Query for pairs within threshold
        # returns set of (i, j) where i < j
        pairs = tree.query_pairs(r=threshold_km)

        if pairs:
            timestamp = t.utc_strftime("%H:%M:%S")
            for i, j in pairs:
                s1 = current_sats[i]
                s2 = current_sats[j]

                # Calculate exact distance
                p1 = np.array(positions[i])
                p2 = np.array(positions[j])
                dist = np.linalg.norm(p1 - p2)

                # Format names with ML tags if available
                def get_label(s):
                    name = s.name
                    stype = getattr(s, "pred_type", None)
                    return f"{name} ({stype})" if stype else name

                alert_msg = (
                    f"🔴 COLLISION ALERT: {get_label(s1)} ⚔️ {get_label(s2)} "
                    f"| Dist: {dist:.2f} km | Time: {timestamp}"
                )
                alerts.add(alert_msg)

    unique_alerts = sorted(list(alerts))

    if verbose:
        if unique_alerts:
            for a in unique_alerts:
                print(a)
        else:
            print("✔ No collisions detected.")

    return unique_alerts
