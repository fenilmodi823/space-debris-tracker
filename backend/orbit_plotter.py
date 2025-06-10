import pyvista as pv
import numpy as np
from skyfield.api import load, wgs84

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
    time_steps = [t0 + i * step_seconds for i in range((minutes * 60) // step_seconds)]

    plotter = pv.Plotter(window_size=(1000, 700))
    plotter.set_background("black")

    # Earth
    earth_radius = 6371.0  # km
    earth = pv.Sphere(radius=earth_radius, theta_resolution=60, phi_resolution=60)
    plotter.add_mesh(earth, color='blue', opacity=0.5, name='Earth')

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

    # === Satellite Picker Logic ===
    def on_pick(picked_point):
        print("\n📡 Satellite Clicked!")
        print(f"Picked Location: {picked_point}")

        for sat in satellites:
            try:
                geo = sat.at(ts.now())
                x, y, z = geo.position.km
                dist = np.linalg.norm(np.array([x, y, z]) - picked_point)
                if dist < 300:  # Close enough to be this satellite
                    subpoint = wgs84.subpoint(geo)
                    print(f"Name      : {sat.name}")
                    print(f"Altitude  : {geo.distance().km:.2f} km")
                    print(f"Latitude  : {subpoint.latitude.degrees:.2f}°")
                    print(f"Longitude : {subpoint.longitude.degrees:.2f}°")
                    print("-" * 30)
                    break
            except:
                continue

    # Enable click picking
    plotter.enable_point_picking(callback=on_pick, show_message=True, use_mesh=True)
    plotter.add_axes()
    plotter.show()
