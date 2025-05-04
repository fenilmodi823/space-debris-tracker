import requests
import os

def fetch_tle(save_path="data/latest_tle.txt"):
    """
    Fetches the latest TLE data from Celestrak and saves it to a file.
    """
    url = "https://celestrak.com/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle"

    try:
        response = requests.get(url)
        response.raise_for_status()
        tle_data = response.text

        # Ensure the data directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w") as file:
            file.write(tle_data)

        print(f"TLE data fetched and saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch TLE data: {e}")

if __name__ == "__main__":
    fetch_tle()
