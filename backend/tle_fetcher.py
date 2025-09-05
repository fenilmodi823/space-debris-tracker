import requests
import os
import sys

# ----------------------------
# Configuration
# ----------------------------
TLE_URL = "https://celestrak.org/NORAD/elements/gp.php"
DEFAULT_GROUP = "last-30-days"  # broader, more useful for ML
FORMAT = "tle"

# ----------------------------
# TLE Fetching Function
# ----------------------------
def fetch_tle(save_path="data/latest_tle.txt", group=DEFAULT_GROUP):
    """
    Fetches the latest TLE data from CelesTrak for a given group and saves it to a local file.

    Parameters:
        save_path (str): The file path to save the TLE data.
        group (str): The satellite group to fetch TLEs for. Default is 'last-30-days'.
    """
    url = f"{TLE_URL}?GROUP={group}&FORMAT={FORMAT}"

    print(f"[INFO] Fetching TLE data for group: {group}")
    print(f"[INFO] Source: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        tle_data = response.text.strip()  # normalize blank lines

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the file
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(tle_data + "\n")

        print(f"[✔] TLE data saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"[✖] Failed to fetch TLE data: {e}")

# ----------------------------
# CLI Execution
# ----------------------------
if __name__ == "__main__":
    group = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_GROUP
    fetch_tle(group=group)
