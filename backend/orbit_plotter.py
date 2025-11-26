import os
import warnings
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pyvista as pv
from skyfield.api import load, wgs84

# Prefer ML colors if available; keep these if used elsewhere
from backend.utils import is_famous_satellite

# Silence a noisy cartopy/pyproj warning seen during projections
warnings.filterwarnings("ignore", message=".*converting a masked element to nan.*")

# ---------------------------
# Configuration
# ---------------------------
EARTH_RADIUS_KM = 6371.0
SECONDS_PER_DAY = 86400

# Assets
TEXTURES_DIR = os.path.join("assets", "textures")
EARTH_DAY_TEX = os.path.join(TEXTURES_DIR, "earth_day.jpg")
CLOUDS_TEX = os.path.join(TEXTURES_DIR, "clouds.png")

MODELS_DIR = "models"

# Map uppercase name -> (filepath, scale_factor)
# Scale is a visual scale (km units in this scene) so sats are visible.
SAT_MODELS: Dict[str, Tuple[str, float]] = {
    "ISS (ZARYA)": (os.path.join(MODELS_DIR, "iss.obj"), 40),
    "HUBBLE SPACE TELESCOPE": (os.path.join(MODELS_DIR, "hubble.obj"), 25),
    "LANDSAT 8": (os.path.join(MODELS_DIR, "landsat8.obj"), 18),
    "SENTINEL-2A": (os.path.join(MODELS_DIR, "sentinel2a.obj"), 18),
    # Add more as you acquire models
}

# Preferred colors come from ML; these are only fallbacks
FAMOUS_SAT_COLORS: Dict[str, str] = {
    "ISS (ZARYA)": "white",
    "HUBBLE SPACE TELESCOPE": "violet",
    "LANDSAT 8": "green",
    "SENTINEL-2A": "cyan",
    # Keep a generic Starlink label if needed
    "STARLINK-30000": "blue",
}

ALTITUDE_RINGS: List[Tuple[float, str, float, str]] = [
    (2000, "limegreen", 0.25, "LEO"),
    (20000, "gold", 0.2, "MEO"),
    (35786, "skyblue", 0.2, "GEO"),
]

# Map for a tiny on-screen legend
ML_LEGEND_TEXT = "ML Colors:  Payload=Green   Rocket Body=Yellow   Debris=Red"


def _prefer_ml_color(sat: Any, orbit_color: str) -> Any:
    """
    Color priority: ML prediction color > famous-sat color > orbit tier color.
    sat.pred_color may be a tuple (r, g, b) or a matplotlib-like color.
    """
    ml_color = getattr(sat, "pred_color", None)
    if ml_color:
        return ml_color
    name_upper = getattr(sat, "name", "").upper()
    return FAMOUS_SAT_COLORS.get(name_upper, orbit_color)


def classify_orbit(alt_km: float) -> Tuple[str, str]:
    if alt_km < 2000:
        return "LEO", "limegreen"
    elif alt_km < 35786:
        return "MEO", "gold"
    else:
        return "GEO", "skyblue"


# ---------------------------
# Textures & Earth helpers
# ---------------------------
def _read_texture(path: str) -> Optional[pv.Texture]:
    try:
        if os.path.exists(path):
            return pv.read_texture(path)
    except Exception:
        pass
    return None


def _add_textured_earth(plotter: pv.Plotter) -> None:
    """Add a textured Earth sphere and optional semi-transparent cloud layer."""
    # Earth sphere with proper UVs
    sphere = pv.Sphere(radius=EARTH_RADIUS_KM, theta_resolution=180, phi_resolution=180)
    sphere.texture_map_to_sphere(inplace=True)

    tex = _read_texture(EARTH_DAY_TEX)
    if tex is not None:
        plotter.add_mesh(sphere, texture=tex, name="Earth")
    else:
        plotter.add_mesh(sphere, color="blue", opacity=0.95, name="Earth")

    # Optional clouds as a slightly larger transparent sphere
    tex_clouds = _read_texture(CLOUDS_TEX)
    if tex_clouds is not None:
        clouds = pv.Sphere(radius=EARTH_RADIUS_KM + 20, theta_resolution=180, phi_resolution=180)
        clouds.texture_map_to_sphere(inplace=True)
        plotter.add_mesh(clouds, texture=tex_clouds, opacity=0.35, name="Clouds")


def _add_orbit_rings(plotter: pv.Plotter) -> List[Any]:
    shell_actors: List[Any] = []
    for alt, color, opacity, label in ALTITUDE_RINGS:
        shell = pv.Sphere(radius=EARTH_RADIUS_KM + alt, theta_resolution=60, phi_resolution=60)
        actor = plotter.add_mesh(shell, color=color, opacity=opacity, name=label)
        shell_actors.append(actor)
    return shell_actors


# ---------------------------
# Model loading
# ---------------------------
def _try_load_sat_model(name_upper: str) -> Optional[Tuple[Any, float]]:
    entry = SAT_MODELS.get(name_upper)
    if not entry:
        return None
    path, scale = entry
    if not os.path.exists(path):
        return None
    try:
        mesh = pv.read(path)
        if getattr(mesh, "n_points", 0) == 0:
            return None
        return mesh, scale
    except Exception:
        return None


# ---------------------------
# Main Visualization Function
# ---------------------------
def plot_satellite_orbits_3d(
    satellites: List[Any],
    minutes: int = 30,
    step_seconds: int = 60,
    max_satellites: int = 10,
) -> None:
    """
    Render Earth, satellite orbits, and info overlays in 3D using PyVista.
    """
    if not satellites:
        print("No satellites to visualize.")
        return

    # Clamp number of satellites to keep the scene readable
    satellites = satellites[: max(1, int(max_satellites))]

    ts = load.timescale()
    t0 = ts.now()
    n_steps = max(2, (minutes * 60) // max(1, int(step_seconds)))
    time_steps = [t0 + (i * step_seconds) / SECONDS_PER_DAY for i in range(n_steps)]

    plotter: pv.Plotter = pv.Plotter(window_size=[1000, 700])
    plotter.set_background(color="black")  # type: ignore[call-arg]

    # Textured Earth + rings
    _add_textured_earth(plotter)
    shells = _add_orbit_rings(plotter)

    # simple color legend
    plotter.add_text(ML_LEGEND_TEXT, position="lower_right", font_size=10, color="white", shadow=True)

    _add_satellites_and_trails(plotter, satellites, ts, time_steps, shells)
    plotter.add_axes()  # type: ignore[call-arg]

    # Controls card
    plotter.add_text(
        "🛰 Controls:\n"
        "R – Toggle orbital rings\n"
        "S – Save screenshot\n"
        "Click – Show satellite info\n"
        "ESC – Exit visualization",
        position="lower_left",
        font_size=10,
        color="white",
        shadow=True,
    )

    # Save a high-res screenshot with 'S'
    def _save_screenshot() -> None:
        os.makedirs("screenshots", exist_ok=True)
        fn = os.path.join("screenshots", f"orbit_view_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png")
        # return_img=False avoids returning a numpy array; intended behavior here.
        plotter.screenshot(fn, return_img=False)
        print(f"[💾] Saved screenshot: {fn}")

    # Wrap callbacks in lambda so Pylance infers correct no-arg signature
    plotter.add_key_event("s", _save_screenshot)  # type: ignore[arg-type]
    plotter.show()


# ---------------------------
# Satellites and Trails
# ---------------------------
def _add_satellites_and_trails(
    plotter: pv.Plotter,
    satellites: List[Any],
    ts: Any,
    time_steps: List[Any],
    shells: List[Any],
) -> None:
    info_text_actor: Optional[Any] = None  # To track overlay text

    def on_pick(picked_point: np.ndarray) -> None:
        nonlocal info_text_actor
        for sat in satellites:
            try:
                geo = sat.at(ts.now())
                pos = geo.position.km
                dist = np.linalg.norm(np.array(pos) - picked_point)
                if dist < 300:
                    subpoint = wgs84.subpoint(geo)

                    # Estimate velocity (finite difference over 1s)
                    t1 = ts.now()
                    t2 = t1 + 1  # +1 second (Skyfield supports adding seconds)
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

    # Build trails and add meshes
    for sat in satellites:
        # Build trail in ECI km
        try:
            trail = [sat.at(t).position.km for t in time_steps]
        except Exception:
            continue
        if len(trail) < 2:
            continue

        trail_arr = np.array(trail)
        x, y, z = trail_arr[-1]
        label_pos = (x, y, z + 300)

        # Auto-focus camera on ISS once
        if "ISS" in sat.name.upper():
            try:
                plotter.camera_position = "xy"
                plotter.camera.focus = [x, y, z]
                plotter.camera.position = [x + 3000, y + 3000, z + 1500]
                plotter.camera.zoom(1.2)
                # Use VTK camera method for azimuth rotation
                plotter.camera.Azimuth(45)
            except Exception:
                pass

        name_upper = sat.name.upper()
        alt_km = np.linalg.norm([x, y, z]) - EARTH_RADIUS_KM
        orbit_type, orbit_color = classify_orbit(float(alt_km))

        # ----- Color priority: ML > famous > orbit tier -----
        color = _prefer_ml_color(sat, orbit_color)

        # Try a real 3D model first; fall back to a small sphere
        maybe_model = _try_load_sat_model(name_upper)
        if maybe_model:
            mesh, scale = maybe_model
            mesh = mesh.copy()
            mesh.translate([x, y, z], inplace=True)
            mesh.scale([scale, scale, scale], inplace=True)
            plotter.add_mesh(mesh)  # use model's own material/texture if it has any
        else:
            # fallback tiny sphere (visual scale; realistic size would be invisible)
            radius = 120 if is_famous_satellite(sat.name) else 80
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
        orbit_line = pv.Spline(trail_arr, 1000)
        plotter.add_mesh(orbit_line, color=color, line_width=2)

    # PyVista 0.43+ uses enable_point_picking; use_picker kw avoids older 'use_mesh' flag.
    plotter.enable_point_picking(callback=on_pick, show_message=True, use_picker=True)  # type: ignore[arg-type]

    def toggle_shells() -> None:
        for actor in shells:
            # VTK Actor methods; keep try/except to cover backend differences
            try:
                actor.SetVisibility(not actor.GetVisibility())
            except Exception:
                pass

    # Wrap in lambda to make the callback explicitly no-arg for the type checker
    plotter.add_key_event("r", toggle_shells)  # type: ignore[arg-type]
