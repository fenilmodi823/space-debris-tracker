from skyfield.api import EarthSatellite, load, wgs84

def load_tles(file_path="data/latest_tle.txt"):
    """
    Loads TLE data from a file and returns a list of EarthSatellite objects.
    """
    satellites = []
    ts = load.timescale()

    try:
        with open(file_path, "r") as file:
            lines = [line.strip() for line in file if line.strip()]  # Remove blank lines

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
        print(f"TLE file '{file_path}' not found.")

    return satellites


def load_famous_sats(tle_path="data/famous_tles/famous.txt"):
    """
    Loads well-known satellites (ISS, Hubble, etc.) from a separate TLE file.
    """
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

        print(f"Loaded {len(sats)} famous satellites from TLE file.")

    except FileNotFoundError:
        print(f"Famous TLE file '{tle_path}' not found.")

    return sats


def print_positions(satellites):
    """
    Prints current lat/lon of satellites (max 10) for quick verification.
    """
    ts = load.timescale()
    t = ts.now()
    count = 0

    for sat in satellites:
        try:
            geocentric = sat.at(t)
            subpoint = wgs84.subpoint(geocentric)

            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees

            if not (lat != lat or lon != lon):  # Not NaN
                print(f"{sat.name}: lat={lat:.2f}, lon={lon:.2f}")
                count += 1

            if count >= 10:
                break

        except Exception:
            continue
