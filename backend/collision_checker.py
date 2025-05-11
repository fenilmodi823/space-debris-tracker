from skyfield.api import load
from itertools import combinations
import numpy as np

def check_collisions(satellites, threshold_km=10, minutes=3000, step_seconds=30):
    """
    Checks all satellite pairs for potential close approaches within the next 'minutes'.
    Prints alerts if predicted distance drops below 'threshold_km'.
    """
    ts = load.timescale()
    t0 = ts.now()
    time_steps = [t0 + i * step_seconds for i in range((minutes * 60) // step_seconds)]

    print(f"Checking {len(satellites)} satellites for next {minutes} minutes...")

    # Precompute positions
    sat_positions = []
    for sat in satellites:
        track = []
        try:
            for t in time_steps:
                track.append(np.array(sat.at(t).position.km))
            sat_positions.append((sat.name, track))
        except:
            continue

    # Compare all pairs
    for (name1, track1), (name2, track2) in combinations(sat_positions, 2):
        min_dist = float('inf')
        min_t_index = -1
        for i, (pos1, pos2) in enumerate(zip(track1, track2)):
            dist = np.linalg.norm(pos1 - pos2)
            if dist < min_dist:
                min_dist = dist
                min_t_index = i

        if min_dist < threshold_km:
            time_of_close = time_steps[min_t_index].utc_strftime('%H:%M:%S')
            print(f"⚠️  Close approach: {name1} ↔ {name2} — {min_dist:.2f} km at {time_of_close}")
