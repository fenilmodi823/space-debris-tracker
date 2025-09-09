# orbit_predictor.py
# Loads general & famous satellites from TLEs (online & offline) and prints positions

from __future__ import annotations

import urllib.parse
import requests
from skyfield.api import EarthSatellite, load, wgs84

# --------------------------------------------------------------------
# Famous satellites (by NAME as listed in CelesTrak)
# You can edit/extend this list freely.
# --------------------------------------------------------------------
FAMOUS_SAT_NAMES = [
    "ISS (ZARYA)",
    "HUBBLE SPACE TELESCOPE",
    "LANDSAT 8",
    "SENTINEL-2A",
    "STARLINK-1130",  # pick a real Starlink (example)
]

CELESTRAK_GP_BASE = "https://celestrak.org/NORAD/elements/gp.php"


def _attach_tle_metadata(sat: EarthSatellite, line1: str, line2: str) -> EarthSatellite:
    """Attach raw TLE lines so the ML code in main.py can parse features."""
    setattr(sat, "line1", line1)
    setattr(sat, "line2", line2)
    return sat


def _fetch_tle_by_name(name: str, timeout: int = 30) -> tuple[str, str] | None:
    """
    Fetch a specific satellite's TLE by NAME using CelesTrak gp.php.
    Returns (line1, line2) or None if not found/invalid.
    """
    url = f"{CELESTRAK_GP_BASE}?NAME={urllib.parse.quote(name)}&FORMAT=tle"
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        lines = [ln.strip() for ln in r.text.splitlines() if ln.strip()]
        # Expect sequences of 3 lines: NAME, L1, L2 (there can be multiple entries)
        for i in range(len(lines) - 2):
            if lines[i].upper() == name.upper() and lines[i + 1].startswith("1 ") and lines[i + 2].startswith("2 "):
                return lines[i + 1], lines[i + 2]
        return None
    except Exception:
        return None


# --------------------------------------------------------------------
# Load general satellite TLEs from local file
# --------------------------------------------------------------------
def load_tles(file_path: str = "data/latest_tle.txt"):
    """
    Load satellites from a local TLE file. Supports:
      - 3-line format (NAME, L1, L2)
      - 2-line format (L1, L2) with UNKNOWN name
    """
    satellites = []
    ts = load.timescale()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]

        i = 0
        while i <= len(lines) - 2:
            # 3-line pattern: NAME, line1, line2
            if i + 2 < len(lines) and lines[i + 1].startswith("1 ") and lines[i + 2].startswith("2 "):
                name = lines[i]
                line1 = lines[i + 1]
                line2 = lines[i + 2]
                i += 3
            # 2-line pattern: line1, line2 (no name available)
            elif lines[i].startswith("1 ") and lines[i + 1].startswith("2 "):
                name = "UNKNOWN"
                line1 = lines[i]
                line2 = lines[i + 1]
                i += 2
            else:
                i += 1
                continue

            try:
                sat = EarthSatellite(line1, line2, name, ts)
                satellites.append(_attach_tle_metadata(sat, line1, line2))
            except Exception:
                # Skip invalid TLEs but continue parsing
                continue

        print(f"Loaded {len(satellites)} satellites from TLE file.")

    except FileNotFoundError:
        print(f"TLE file '{file_path}' not found.")

    return satellites


# --------------------------------------------------------------------
# Load famous satellites from online sources (preferred)
# Falls back to local file if online fetch yields none
# --------------------------------------------------------------------
def load_famous_sats(names: list[str] | None = None, fallback_path: str = "data/famous_tles/famous.txt"):
    """
    Try to load a curated set of famous satellites by NAME from CelesTrak (online).
    If none could be loaded, fall back to local file.
    """
    ts = load.timescale()
    sats = []
    names = names or FAMOUS_SAT_NAMES

    # Online fetch by NAME
    for name in names:
        pair = _fetch_tle_by_name(name)
        if pair is None:
            print(f"Failed to fetch TLE for {name}")
            continue
        line1, line2 = pair
        try:
            sat = EarthSatellite(line1, line2, name, ts)
            sats.append(_attach_tle_metadata(sat, line1, line2))
        except Exception as e:
            print(f"Invalid TLE for {name}: {e}")

    if sats:
        print(f"Loaded {len(sats)} famous satellites from online sources.")
        return sats

    # Fallback to local file
    print("No famous satellites loaded online; trying local fallback...")
    return load_famous_sats_from_file(fallback_path)


# --------------------------------------------------------------------
# Fallback: Load famous satellites from local file
# --------------------------------------------------------------------
def load_famous_sats_from_file(tle_path: str = "data/famous_tles/famous.txt"):
    ts = load.timescale()
    sats = []

    try:
        with open(tle_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        for i in range(0, len(lines) - 2, 3):
            name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]
            try:
                sat = EarthSatellite(line1, line2, name, ts)
                sats.append(_attach_tle_metadata(sat, line1, line2))
            except Exception:
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
