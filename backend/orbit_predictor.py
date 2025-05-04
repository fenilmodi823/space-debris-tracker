from skyfield.api import EarthSatellite, load

def load_tles(file_path="data/latest_tle.txt"):
    """
    Loads TLE data from a file and returns a list of EarthSatellite objects.
    """
    satellites = []

    # Load timescale
    ts = load.timescale()

    try:
        with open(file_path, "r") as file:
            lines = [line.strip() for line in file if line.strip()]  # Remove blank lines

        # Group lines into sets of 3 (name, line1, line2)
        for i in range(0, len(lines) - 2, 3):
            name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]

            if len(line1) > 0 and len(line2) > 0:
                try:
                    sat = EarthSatellite(line1, line2, name, ts)
                    satellites.append(sat)
                except ValueError:
                    # Skip bad TLEs
                    continue

        print(f"Loaded {len(satellites)} satellites from TLE file.")

    except FileNotFoundError:
        print(f"TLE file {file_path} not found.")

    return satellites

def print_positions(satellites):
    """
    Prints current positions (latitude, longitude) of the satellites.
    Skips satellites with invalid positions.
    """
    ts = load.timescale()
    t = ts.now()

    count = 0
    for sat in satellites:
        try:
            geocentric = sat.at(t)
            subpoint = geocentric.subpoint()

            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees

            if not (lat != lat or lon != lon):
                print(f"{sat.name}: lat={lat:.2f}, lon={lon:.2f}")
                count += 1

            if count >= 10:
                break

        except Exception as e:
            continue  # Skip satellites that raise errors
