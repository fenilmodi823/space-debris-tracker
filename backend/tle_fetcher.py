import requests
import os

# ----------------------------
# Configuration
# ----------------------------
TLE_URL = "https://celestrak.com/NORAD/elements/gp.php"
DEFAULT_GROUP = "gps-ops"
FORMAT = "tle"

# ----------------------------
# TLE Fetching Function
# ----------------------------
def fetch_tle(save_path="data/latest_tle.txt", group=DEFAULT_GROUP):
    """
    Fetches the latest TLE data from Celestrak for a given group and saves it to a local file.

    Parameters:
        save_path (str): The file path to save the TLE data.
        group (str): The satellite group to fetch TLEs for. Default is 'gps-ops'.
    """
    url = f"{TLE_URL}?GROUP={group}&FORMAT={FORMAT}"

    print(f"[INFO] Fetching TLE data for group: {group}")
    print(f"[INFO] Source: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        tle_data = response.text

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the file
        with open(save_path, "w") as file:
            file.write(tle_data)

        print(f"[✔] TLE data saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"[✖] Failed to fetch TLE data: {e}")

# ----------------------------
# CLI Execution
# ----------------------------
if __name__ == "__main__":
    fetch_tle()
