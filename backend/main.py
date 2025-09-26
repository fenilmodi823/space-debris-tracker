# === Space Debris Tracker: Main Script ===
# Orchestrates TLE fetching, satellite loading, ML annotation,
# collision checking, and visualization (2D live & 3D).

import os
import re
import joblib
import numpy as np

from backend import tle_fetcher
from backend import orbit_predictor
from backend import visualizer
from backend import collision_checker
from backend import orbit_plotter
from backend.orbit_predictor import load_famous_sats


# --------------------------
# Tunables
# --------------------------
COLLISION_MAX = 60    # cap pairwise collision check set size
PLOT3D_MAX    = 120   # cap for 3D plotting
LIVE2D_MAX    = 100   # cap for live 2D animation

# --------------------------
# ML: load once at startup
# --------------------------
MODEL_PATH = os.path.join("ml_models", "object_classifier.joblib")
try:
    MODEL_BUNDLE = joblib.load(MODEL_PATH)
    CLF       = MODEL_BUNDLE["model"]
    FEATURES  = MODEL_BUNDLE.get("features", ["inc_deg", "ecc", "mm_rev_day", "bstar"])
    CLASSES   = list(MODEL_BUNDLE.get("classes_", []))
    print(f"[ML] Loaded model from {MODEL_PATH} with classes: {CLASSES}")
except Exception as e:
    print(f"[ML] Could not load model: {e}")
    CLF, FEATURES, CLASSES = None, [], []

TYPE_COLOR = {
    "Payload": (0.20, 0.90, 0.20),     # green
    "Rocket Body": (1.00, 0.90, 0.20), # yellow
    "Debris": (1.00, 0.30, 0.30),      # red
    "Unknown": (0.80, 0.80, 0.80),     # grey fallback
}

# --------------------------
# Helpers for ML features
# --------------------------
def _parse_bstar(line1: str):
    """BSTAR from TLE line 1 (cols 54-61, implied decimal/exponent)."""
    try:
        mant = line1[53:59].strip()
        expo = line1[59:61].strip()
        m = re.match(r"^([ +\-]?)(\d+)$", mant)
        if not m:
            return float("nan")
        sign, digits = m.groups()
        mantissa = float(f"{sign}0.{digits}")
        exponent = int(expo)
        return mantissa * (10.0 ** exponent)
    except Exception:
        return float("nan")

def _features_from_tle_lines(line1: str, line2: str):
    """Return (inc_deg, ecc, mm_rev_day, bstar) parsed from 2 TLE lines."""
    try:
        inc_deg     = float(line2[8:16])
        ecc_txt     = line2[26:33].strip()
        ecc         = float(f"0.{ecc_txt}") if ecc_txt else float("nan")
        mm_rev_day  = float(line2[52:63])
        bstar       = _parse_bstar(line1)
        return inc_deg, ecc, mm_rev_day, bstar
    except Exception:
        return float("nan"), float("nan"), float("nan"), float("nan")

def classify_and_color(props: dict):
    """
    props must contain: inc_deg, ecc, mm_rev_day, bstar (float-able).
    Returns: (label, prob, rgb_tuple)
    """
    if not CLF:
        return "Unknown", 0.0, TYPE_COLOR["Unknown"]
    try:
        vec = np.array([[float(props["inc_deg"]),
                         float(props["ecc"]),
                         float(props["mm_rev_day"]),
                         float(props["bstar"])]], dtype=float)
    except Exception:
        return "Unknown", 0.0, TYPE_COLOR["Unknown"]

    # Predict + probability
    try:
        pred = CLF.predict(vec)[0]
        prob = float(CLF.predict_proba(vec).max()) if hasattr(CLF, "predict_proba") else 1.0
    except Exception:
        return "Unknown", 0.0, TYPE_COLOR["Unknown"]

    return pred, prob, TYPE_COLOR.get(pred, TYPE_COLOR["Unknown"])

def extract_features_from_sat(sat):
    """
    Tries attributes first (inc_deg/ecc/mm_rev_day/bstar).
    If unavailable, tries TLE parsing via sat.line1/sat.line2 or sat.tle[0]/sat.tle[1].
    Returns dict with keys: inc_deg, ecc, mm_rev_day, bstar (floats or NaN).
    """
    # 1) Direct attributes on sat (if your loader set them)
    for key in ("inc_deg", "ecc", "mm_rev_day", "bstar"):
        if hasattr(sat, key):
            try:
                _ = float(getattr(sat, key))
            except Exception:
                break
        else:
            break
    else:
        # All four present and float-able
        return {
            "inc_deg": float(getattr(sat, "inc_deg")),
            "ecc": float(getattr(sat, "ecc")),
            "mm_rev_day": float(getattr(sat, "mm_rev_day")),
            "bstar": float(getattr(sat, "bstar")),
        }

    # 2) Parse from TLE strings if available
    line1 = getattr(sat, "line1", None)
    line2 = getattr(sat, "line2", None)
    if line1 and line2:
        inc_deg, ecc, mm_rev_day, bstar = _features_from_tle_lines(line1, line2)
        return {"inc_deg": inc_deg, "ecc": ecc, "mm_rev_day": mm_rev_day, "bstar": bstar}

    # Some loaders keep TLE in a list/tuple
    tle = getattr(sat, "tle", None)
    if isinstance(tle, (list, tuple)) and len(tle) >= 2:
        inc_deg, ecc, mm_rev_day, bstar = _features_from_tle_lines(tle[0], tle[1])
        return {"inc_deg": inc_deg, "ecc": ecc, "mm_rev_day": mm_rev_day, "bstar": bstar}

    # 3) Could not get features
    return {"inc_deg": float("nan"), "ecc": float("nan"),
            "mm_rev_day": float("nan"), "bstar": float("nan")}

def annotate_satellites_with_ml(satellites):
    """
    For each satellite:
      - extract features
      - run classifier
      - attach: sat.pred_type, sat.pred_conf, sat.pred_color
    Prints a short summary by class.
    """
    counts = {"Payload": 0, "Rocket Body": 0, "Debris": 0, "Unknown": 0}
    for sat in satellites:
        feats = extract_features_from_sat(sat)
        label, prob, color = classify_and_color(feats)
        # attach attributes dynamically
        setattr(sat, "pred_type", label)
        setattr(sat, "pred_conf", prob)
        setattr(sat, "pred_color", color)
        counts[label] = counts.get(label, 0) + 1

    print("ML classification summary:")
    for k in ("Payload", "Rocket Body", "Debris", "Unknown"):
        print(f" - {k}: {counts.get(k, 0)}")
    print()

def main():
    print("=== Space Debris Tracker ===\n")

    # ------------------------------------------
    # Step 1: Fetch latest TLE data
    # ------------------------------------------
    print("[1/4] Fetching latest TLE data...")
    tle_fetcher.fetch_tle()
    print("✔ TLE data saved to data/latest_tle.txt\n")

    # ------------------------------------------
    # Step 2: Load satellites (famous + many from file)
    # ------------------------------------------
    print("[2/4] Loading famous satellites from Celestrak...")
    famous = load_famous_sats()

    # Load a larger batch from the freshly saved file
    general = orbit_predictor.load_tles("data/latest_tle.txt")

    # Merge and dedupe by name (simple, effective)
    sat_by_name = {getattr(s, "name", "UNKNOWN"): s for s in (famous + general)}
    satellites = list(sat_by_name.values())

    if not satellites:
        print("No satellites loaded. Check TLE fetch or fallback.")
        return

    print("Satellites loaded:")
    for sat in satellites[:20]:
        print(" -", getattr(sat, "name", "UNKNOWN"))
    if len(satellites) > 20:
        print(f" ... and {len(satellites) - 20} more")
    print(f"✔ Total satellites loaded: {len(satellites)}\n")

    # ------------------------------------------
    # Step 2.5: Classify & annotate with ML
    # ------------------------------------------
    if CLF:
        annotate_satellites_with_ml(satellites)
    else:
        print("[ML] Model not available; skipping classification.\n")

    # ------------------------------------------
    # Step 3: Collision prediction (cap set size)
    # ------------------------------------------
    print("[3/4] Checking for close approaches...")
    if len(satellites) >= 2:
        subset = satellites[:COLLISION_MAX]
        if len(satellites) > COLLISION_MAX:
            print(f"[i] Using first {COLLISION_MAX} satellites for collision check (cap).")
        collision_checker.check_collisions(subset, threshold_km=10)
    else:
        print("Skipping collision check (need at least 2 satellites).")
    print("✔ Collision analysis complete.\n")

    # ------------------------------------------
    # Step 4: Visualization (2D live + 3D)
    # ------------------------------------------
    print("[4/4] Visualizing satellite orbits...")

    # 2D: Live animation until window close (show many satellites)
    visualizer.plot_animated_positions_live(satellites, interval_ms=200, max_sats=LIVE2D_MAX)

    # 3D: Use a capped subset for smooth interaction
    orbit_plotter.plot_satellite_orbits_3d(satellites[:PLOT3D_MAX])

    print("✔ Visualizations complete.")

# Run the program
if __name__ == "__main__":
    main()
