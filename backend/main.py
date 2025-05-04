from backend import tle_fetcher

def main():
    print("=== Space Debris Tracker ===")
    print("Fetching latest TLE data...")

    tle_fetcher.fetch_tle()

    print("TLE data fetched successfully.")
    # Next steps will go here (orbit prediction, visualization, etc.)

if __name__ == "__main__":
    main()
