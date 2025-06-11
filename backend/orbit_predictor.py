# orbit_predictor.py
# Loads general & famous satellites from TLEs (online & offline) and prints positions

from skyfield.api import EarthSatellite, load, wgs84
import requests

# --------------------------------------------------------------------
# Online real-time TLE sources for famous satellites
# --------------------------------------------------------------------
FAMOUS_SAT_URLS = {
    "ISS (ZARYA)": "https://celestrak.org/NORAD/elements/stations.txt",
    "HUBBLE SPACE TELESCOPE": "https://celestrak.org/NORAD/elements/science.txt",
    "LANDSAT 8": "https://celestrak.org/NORAD/elements/earth-resources.txt",
    "SENTINEL-2A": "https://celestrak.org/NORAD/elements/earth-resources.txt",
    "STARLINK-30000": "https://celestrak.org/NORAD/elements/starlink.txt",
}

# --------------------------------------------------------------------
# Load general satellite TLEs from local file
# --------------------------------------------------------------------
def load_tles(file_path="data/latest_tle.txt"):
    satellites = []
    ts = load.timescale()

    try:
        with open(file_path, "r") as file:
            lines = [line.strip() for line in file if line.strip()]

        for i in range(0, len(lines) - 2, 3):
            name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]

            if line1 and line2:
                try:
                    sat = EarthSatellite(line1, line2, name, ts)
                    satellites.append(sat)
                except ValueError:
                    continue  # Skip invalid TLE entries

        print(f"Loaded {len(satellites)} satellites from TLE file.")

    except FileNotFoundError:
        print(f"❌ TLE file '{file_path}' not found.")

    return satellites

# --------------------------------------------------------------------
# Load famous satellites from online sources (real-time preferred)
# --------------------------------------------------------------------
def load_famous_sats():
    ts = load.timescale()
    sats = []

    for name, url in FAMOUS_SAT_URLS.items():
        try:
            response = requests.get(url)
            lines = response.text.strip().splitlines()

            # Find satellite entry
            for i in range(len(lines) - 2):
                if name.upper() in lines[i].upper():
                    sat_name = lines[i].strip()
                    line1 = lines[i + 1].strip()
                    line2 = lines[i + 2].strip()
                    sat = EarthSatellite(line1, line2, sat_name, ts)
                    sats.append(sat)
                    break

        except Exception as e:
            print(f"Failed to fetch TLE for {name}: {e}")

    print(f"Loaded {len(sats)} famous satellites from online sources.")
    return sats

# --------------------------------------------------------------------
# Fallback: Load famous satellites from local file
# --------------------------------------------------------------------
def load_famous_sats_from_file(tle_path="data/famous_tles/famous.txt"):
    sats = []
    ts = load.timescale()

    try:
        with open(tle_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            for i in range(0, len(lines) - 2, 3):
                name = lines[i]
                line1 = lines[i + 1]
                line2 = lines[i + 2]
                try:
                    sat = EarthSatellite(line1, line2, name, ts)
                    sats.append(sat)
                except ValueError:
                    continue

        print(f"Loaded {len(sats)} famous satellites from fallback file.")

    except FileNotFoundError:
        print(f"Famous TLE file '{tle_path}' not found.")

    return sats

# --------------------------------------------------------------------
# Quick print of satellite lat/lon positions
# --------------------------------------------------------------------
def print_positions(satellites):
    ts = load.timescale()
    t = ts.now()
    count = 0

    for sat in satellites:
        try:
            geocentric = sat.at(t)
            subpoint = wgs84.subpoint(geocentric)

            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees

            if not (lat != lat or lon != lon):  # Skip NaN
                print(f"{sat.name}: lat={lat:.2f}, lon={lon:.2f}")
                count += 1

            if count >= 10:
                break
        except Exception:
            continue
