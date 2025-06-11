import pyvista as pv
import numpy as np
from skyfield.api import load, wgs84
from datetime import datetime

# Custom render settings for well-known satellites
FAMOUS_SAT_COLORS = {
    "ISS (ZARYA)": "white",
    "HUBBLE SPACE TELESCOPE": "violet",
    "LANDSAT 8": "green",
    "SENTINEL-2A": "cyan",
    "STARLINK-30000": "blue"
}

def plot_satellite_orbits_3d(satellites, minutes=30, step_seconds=60):
    """
    Plots Earth, satellite positions, orbital trails, labels, and click interactivity using PyVista.
    """
    ts = load.timescale()
    t0 = ts.now()
    # Convert step_seconds from seconds to days when adding to the Skyfield Time
    # object, otherwise each step would advance by that many **days**.
    seconds_per_day = 86400
    time_steps = [t0 + (i * step_seconds) / seconds_per_day
                  for i in range((minutes * 60) // step_seconds)]

    plotter = pv.Plotter(window_size=(1000, 700))
    plotter.set_background("black")

    # Earth
    earth_radius = 6371.0  # km
    earth = pv.Sphere(radius=earth_radius, theta_resolution=60, phi_resolution=60)
    plotter.add_mesh(earth, color='blue', opacity=0.5, name='Earth')    

    # Altitude rings
    altitude_rings = [
        (2000, 'limegreen', 0.25, "LEO"),
        (20000, 'gold', 0.2, "MEO"),
        (35786, 'skyblue', 0.2, "GEO")
    ]

    for alt, color, opacity, label in altitude_rings:
        shell = pv.Sphere(radius=earth_radius + alt, theta_resolution=60, phi_resolution=60)
        plotter.add_mesh(shell, color=color, opacity=opacity)

    # Satellites and trails
    for sat in satellites[:10]:  # Limit to avoid lag
        trail = []
        try:
            for t in time_steps:
                pos = sat.at(t).position.km
                trail.append(pos)
        except:
            continue

        if len(trail) < 2:
            continue

        trail = np.array(trail)
        x, y, z = trail[-1]
        label_pos = (x, y, z + 300)

        # Style: famous or default
        sat_name_upper = sat.name.upper()
        color = FAMOUS_SAT_COLORS.get(sat_name_upper, 'red')
        radius = 250 if sat_name_upper in FAMOUS_SAT_COLORS else 150
        trail_color = color if sat_name_upper in FAMOUS_SAT_COLORS else 'yellow'

        # Satellite sphere
        plotter.add_mesh(pv.Sphere(center=(x, y, z), radius=radius), color=color)

        # Satellite label
        plotter.add_point_labels(
            np.array([label_pos]),
            [sat.name],
            font_size=12,
            text_color='white',
            point_color=color,
            point_size=0,
            shape_opacity=0.6,
            render_points_as_spheres=True
        )

        # Orbital trail
        line = pv.Spline(trail, 1000)
        plotter.add_mesh(line, color=trail_color, line_width=2)

        # === Overlay info panel on click ===
        info_text_actor = None  # To keep track of previous text

        def on_pick(picked_point):
            nonlocal info_text_actor  # So we can modify the outer variable
            for sat in satellites:
                try:
                    geo = sat.at(ts.now())
                    pos = geo.position.km
                    dist = np.linalg.norm(np.array(pos) - picked_point)
                    if dist < 300:
                        subpoint = wgs84.subpoint(geo)

                        # Estimate velocity (simple 2-point calc)
                        t1 = ts.now()
                        t2 = t1 + 1  # 1 second later
                        r1 = np.array(sat.at(t1).position.km)
                        r2 = np.array(sat.at(t2).position.km)
                        velocity = np.linalg.norm(r2 - r1)

                        # Info to display
                        info = (
                            f"📡 {sat.name}\n"
                            f"Lat      : {subpoint.latitude.degrees:.2f}°\n"
                            f"Lon      : {subpoint.longitude.degrees:.2f}°\n"
                            f"Alt      : {geo.distance().km:.2f} km\n"
                            f"Velocity : {velocity:.2f} km/s\n"
                            f"Time     : {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                        )

                        # Remove previous text if exists
                        if info_text_actor:
                            plotter.remove_actor(info_text_actor)

                        # Add new info text to the top left
                        info_text_actor = plotter.add_text(info, position='upper_left', font_size=10, color='white')
                        break
                except:
                    continue

    # Enable click picking
    plotter.enable_point_picking(callback=on_pick, show_message=True, use_mesh=True)
    plotter.add_axes()
    plotter.show()
