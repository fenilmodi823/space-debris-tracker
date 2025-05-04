import tle_fetcher
import orbit_predictor
import visualizer  # Same folder imports

def main():
    print("=== Space Debris Tracker ===")
    
    # Step 1: Fetch TLEs
    print("[1/3] Fetching latest TLE data...")
    tle_fetcher.fetch_tle()
    print("TLE data fetched successfully.\n")
    
    # Step 2: Load and predict orbits
    print("[2/3] Loading satellites and computing positions...")
    satellites = orbit_predictor.load_tles()
    orbit_predictor.print_positions(satellites)
    print("Satellite positions computed.\n")

    # Step 3: Visualize orbits
    print("[3/3] Visualizing satellite positions...")
    visualizer.plot_positions(satellites)
    print("Visualization complete.")

if __name__ == "__main__":
    main()
