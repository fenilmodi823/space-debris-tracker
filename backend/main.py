# === Space Debris Tracker: Main Script ===
# This script orchestrates TLE fetching, satellite loading,
# collision checking, and visualization (2D & 3D).

import tle_fetcher
import orbit_predictor
import visualizer
import collision_checker
import orbit_plotter
from orbit_predictor import load_famous_sats

def main():
    print("=== Space Debris Tracker ===\n")

    # ------------------------------------------
    # Step 1: Fetch latest TLE data
    # ------------------------------------------
    print("[1/4] Fetching latest TLE data...")
    tle_fetcher.fetch_tle()
    print("✔ TLE data saved to data/latest_tle.txt\n")

    # ------------------------------------------
    # Step 2: Load famous satellites only
    # ------------------------------------------
    print("[2/4] Loading famous satellites from Celestrak...")
    satellites = load_famous_sats()

    if not satellites:
        print("No satellites loaded. Check TLE fetch or fallback.")
        return

    # Optional: Print loaded satellite names
    print("Satellites loaded:")
    for sat in satellites:
        print(" -", sat.name)
    print(f"✔ Total satellites loaded: {len(satellites)}\n")

    # ------------------------------------------
    # Step 3: Collision prediction
    # ------------------------------------------
    print("[3/4] Checking for close approaches...")
    collision_checker.check_collisions(satellites, threshold_km=10)
    print("✔ Collision analysis complete.\n")

    # ------------------------------------------
    # Step 4: Visualization (2D + 3D)
    # ------------------------------------------
    print("[4/4] Visualizing satellite orbits...")
    visualizer.plot_animated_positions(satellites)
    orbit_plotter.plot_satellite_orbits_3d(satellites)
    print("✔ Visualizations complete.")

# Run the program
if __name__ == "__main__":
    main()
