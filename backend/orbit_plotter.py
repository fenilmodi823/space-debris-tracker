import pyvista as pv
import numpy as np
from skyfield.api import load

# Custom render settings for known satellites
FAMOUS_SAT_COLORS = {
    "ISS (ZARYA)": "white",
    "HUBBLE SPACE TELESCOPE": "violet",
    "LANDSAT 8": "green",
    "SENTINEL-2A": "cyan",
    "STARLINK-30000": "blue"
}

def plot_satellite_orbits_3d(satellites, minutes=30, step_seconds=60):
    """
    Plots Earth, satellite positions, orbital trails, labels, and altitude rings using PyVista.
    """
    ts = load.timescale()
    t0 = ts.now()
    time_steps = [t0 + i * step_seconds for i in range((minutes * 60) // step_seconds)]

    plotter = pv.Plotter(window_size=(1000, 700))
    plotter.set_background("black")

    # Earth radius in km
    earth_radius = 6371.0

    # Draw Earth
    earth = pv.Sphere(radius=earth_radius, theta_resolution=60, phi_resolution=60)
    plotter.add_mesh(earth, color='blue', opacity=0.5, name='Earth')

    # Altitude rings
    """
    altitude_rings = [
        (2000, 'limegreen', 0.25, "LEO"),
        (20000, 'gold', 0.2, "MEO"),
        (35786, 'skyblue', 0.2, "GEO")
    ]
   
    for alt, color, opacity, label in altitude_rings:
        shell = pv.Sphere(radius=earth_radius + alt, theta_resolution=60, phi_resolution=60)
        plotter.add_mesh(shell, color=color, opacity=opacity)
    """
    # Plot satellites
    for sat in satellites[:20]:
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

        # Check if this satellite is in the famous list
        sat_name_upper = sat.name.upper()
        color = FAMOUS_SAT_COLORS.get(sat_name_upper, 'red')
        radius = 250 if sat_name_upper in FAMOUS_SAT_COLORS else 150
        trail_color = color if sat_name_upper in FAMOUS_SAT_COLORS else 'yellow'

        # Draw satellite as a sphere
        plotter.add_mesh(pv.Sphere(center=(x, y, z), radius=radius), color=color)

        # Draw label
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

        # Draw orbital trail
        line = pv.Spline(trail, 1000)
        plotter.add_mesh(line, color=trail_color, line_width=2)
