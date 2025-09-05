import os
from datetime import datetime

import numpy as np
import pyvista as pv
from skyfield.api import load, wgs84

from utils import get_satellite_color, is_famous_satellite  # keep if used elsewhere

# ---------------------------
# Configuration
# ---------------------------
EARTH_RADIUS_KM = 6371.0
SECONDS_PER_DAY = 86400

# Preferred colors come from ML; these are only fallbacks
FAMOUS_SAT_COLORS = {
    "ISS (ZARYA)": "white",
    "HUBBLE SPACE TELESCOPE": "violet",
    "LANDSAT 8": "green",
    "SENTINEL-2A": "cyan",
    "STARLINK-30000": "blue",
}

ALTITUDE_RINGS = [
    (2000, "limegreen", 0.25, "LEO"),
    (20000, "gold", 0.2, "MEO"),
    (35786, "skyblue", 0.2, "GEO"),
]

# Map for a tiny on-screen legend
ML_LEGEND_TEXT = "ML Colors:  Payload=Green   Rocket Body=Yellow   Debris=Red"

def classify_orbit(alt_km):
    if alt_km < 2000:
        return "LEO", "limegreen"
    elif alt_km < 35786:
        return "MEO", "gold"
    else:
        return "GEO", "skyblue"

# ---------------------------
# Main Visualization Function
# ---------------------------
def plot_satellite_orbits_3d(satellites, minutes=30, step_seconds=60, max_satellites=10):
    """
    Render Earth, satellite orbits, and info overlays in 3D using PyVista.
    """
    ts = load.timescale()
    t0 = ts.now()
    time_steps = [t0 + (i * step_seconds) / SECONDS_PER_DAY for i in range((minutes * 60) // step_seconds)]

    plotter = pv.Plotter(window_size=(1000, 700))
    plotter.set_background("black")

    shells = _add_earth_and_rings(plotter)

    # simple color legend
    plotter.add_text(ML_LEGEND_TEXT, position="lower_right", font_size=10, color="white", shadow=True)

    _add_satellites_and_trails(plotter, satellites[:max_satellites], ts, time_steps, shells)
    plotter.add_axes()

    # Controls card
    plotter.add_text(
        "🛰 Controls:\n"
        "R – Toggle orbital rings\n"
        "Click – Show satellite info\n"
        "ESC – Exit visualization",
        position="lower_left",
        font_size=10,
        color="white",
        shadow=True,
    )

    plotter.show()

# ---------------------------
# Earth and Altitude Shells
# ---------------------------
def _add_earth_and_rings(plotter):
    shell_actors = []

    earth = pv.Sphere(radius=EARTH_RADIUS_KM, theta_resolution=60, phi_resolution=60)
    plotter.add_mesh(earth, color="blue", opacity=0.5, name="Earth")

    for alt, color, opacity, label in ALTITUDE_RINGS:
        shell = pv.Sphere(radius=EARTH_RADIUS_KM + alt, theta_resolution=60, phi_resolution=60)
        actor = plotter.add_mesh(shell, color=color, opacity=opacity, name=label)
        shell_actors.append(actor)

    return shell_actors

# ---------------------------
# Satellites and Trails
# ---------------------------
def _add_satellites_and_trails(plotter, satellites, ts, time_steps, shells):
    info_text_actor = None  # To track overlay text

    def on_pick(picked_point):
        nonlocal info_text_actor
        for sat in satellites:
            try:
                geo = sat.at(ts.now())
                pos = geo.position.km
                dist = np.linalg.norm(np.array(pos) - picked_point)
                if dist < 300:
                    subpoint = wgs84.subpoint(geo)

                    # Estimate velocity
                    t1 = ts.now()
                    t2 = t1 + 1
                    r1 = np.array(sat.at(t1).position.km)
                    r2 = np.array(sat.at(t2).position.km)
                    velocity = np.linalg.norm(r2 - r1)

                    # ML info, if present
                    pred_type = getattr(sat, "pred_type", "Unknown")
                    pred_conf = getattr(sat, "pred_conf", 0.0)

                    info = (
                        f"{sat.name}\n"
                        f"Type     : {pred_type} ({pred_conf:.0%})\n"
                        f"Lat      : {subpoint.latitude.degrees:.2f}°\n"
                        f"Lon      : {subpoint.longitude.degrees:.2f}°\n"
                        f"Alt      : {geo.distance().km:.2f} km\n"
                        f"Velocity : {velocity:.2f} km/s\n"
                        f"Time     : {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                    )

                    if info_text_actor:
                        plotter.remove_actor(info_text_actor)

                    info_text_actor = plotter.add_text(info, position="upper_left", font_size=10, color="white")
                    break
            except Exception:
                continue

    for sat in satellites:
        # Build trail in ECI km
        try:
            trail = [sat.at(t).position.km for t in time_steps]
        except Exception:
            continue
        if len(trail) < 2:
            continue

        trail = np.array(trail)
        x, y, z = trail[-1]
        label_pos = (x, y, z + 300)

        # Auto-focus camera on ISS
        if "ISS" in sat.name.upper():
            plotter.camera_position = "xy"
            plotter.set_focus([x, y, z])
            plotter.set_position([x + 3000, y + 3000, z + 1500])
            plotter.camera.zoom(1.2)
            plotter.camera.azimuth += 45

        name_upper = sat.name.upper()
        alt_km = np.linalg.norm([x, y, z]) - EARTH_RADIUS_KM
        orbit_type, orbit_color = classify_orbit(alt_km)

        # ----- Color priority: ML > famous > orbit tier -----
        ml_color = getattr(sat, "pred_color", None)  # tuple like (r,g,b)
        color = ml_color if ml_color else FAMOUS_SAT_COLORS.get(name_upper, orbit_color)

        radius = 250 if is_famous_satellite(sat.name) else 150

        # Render ISS with 3D model, others as spheres
        if "ISS" in name_upper:
            try:
                model_path = os.path.join("models", "iss.obj")
                iss_mesh = pv.read(model_path)

                if iss_mesh.n_points == 0:
                    raise ValueError("Empty ISS model mesh.")

                iss_mesh = iss_mesh.copy()
                iss_mesh.translate([x, y, z], inplace=True)
                iss_mesh.scale([50, 50, 50], inplace=True)
                plotter.add_mesh(iss_mesh, color="white")
                print("✅ ISS 3D model loaded successfully.")
            except Exception as e:
                print(f"⚠ Could not load ISS model: {e}")
                plotter.add_mesh(pv.Sphere(center=(x, y, z), radius=radius), color=color)
        else:
            plotter.add_mesh(pv.Sphere(center=(x, y, z), radius=radius), color=color)

        # Label with orbit type + ML type (if available)
        pred_type = getattr(sat, "pred_type", None)
        pred_conf = getattr(sat, "pred_conf", None)
        if pred_type is not None and pred_conf is not None:
            label = f"{sat.name} ({orbit_type}) • Type: {pred_type} ({pred_conf:.0%})"
        else:
            label = f"{sat.name} ({orbit_type})"

        plotter.add_point_labels(
            np.array([label_pos]),
            [label],
            font_size=12,
            text_color="white",
            point_color=color,
            point_size=0,
            shape_opacity=0.6,
            render_points_as_spheres=True,
        )

        # Trail: prefer ML color for visual consistency
        trail_color = color
        orbit_line = pv.Spline(trail, 1000)
        plotter.add_mesh(orbit_line, color=trail_color, line_width=2)

    # PyVista deprecation fix: use_picker instead of use_mesh
    plotter.enable_point_picking(callback=on_pick, show_message=True, use_picker=True)

    def toggle_shells():
        for actor in shells:
            actor.SetVisibility(not actor.GetVisibility())

    plotter.add_key_event("r", toggle_shells)
