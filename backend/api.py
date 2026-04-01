from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from skyfield.api import load, wgs84
from backend.tle_fetcher import fetch_tle
from backend.orbit_predictor import load_tles

app = FastAPI(title="Space Debris Tracker API")

# Configure CORS to allow the Vite React frontend (typically running on port 5173)
# and allow all origins for ease of development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/satellites")
def get_satellites():
    # 1. Fetch specialized CelesTrak groups
    stations_path, _ = fetch_tle(group="stations")
    gnss_path, _ = fetch_tle(group="gnss")
    geo_path, _ = fetch_tle(group="geo")
    active_path, _ = fetch_tle(group="active")

    # 2. Load into Skyfield EarthSatellite objects
    stations_sats = load_tles(str(stations_path))
    gnss_sats = load_tles(str(gnss_path))
    geo_sats = load_tles(str(geo_path))
    active_sats = load_tles(str(active_path))

    final_satellites = []

    # 3. Explicitly Isolate the ISS and Pin it as Priority #1
    iss_sat = next((s for s in stations_sats if s.name and "ISS" in s.name), None)
    if iss_sat:
        final_satellites.append(iss_sat)

    # 4. Create a Balanced Payload for the 3D Render
    # Append MEO candidates (GNSS)
    final_satellites.extend(gnss_sats[:40])

    # Append GEO candidates
    final_satellites.extend(geo_sats[:40])

    # Append LEO candidates (remaining Active), ensuring ISS is not duplicated
    active_filtered = [s for s in active_sats if s.name and "ISS" not in s.name][:70]
    final_satellites.extend(active_filtered)

    ts = load.timescale()

    result = []
    for sat in final_satellites:
        # We need the TLE metadata to be present (attached by backend.orbit_predictor load_tles)
        if hasattr(sat, "line1") and hasattr(sat, "line2"):
            # Calculate current position for Cesium fallback
            geocentric = sat.at(ts.now())
            subpoint = wgs84.subpoint(geocentric)

            result.append(
                {
                    "name": sat.name,
                    "line1": sat.line1,
                    "line2": sat.line2,
                    "lat": subpoint.latitude.degrees,
                    "lon": subpoint.longitude.degrees,
                    "alt": subpoint.elevation.km,
                    "alert": False,  # Mocked for now
                }
            )

    return result
