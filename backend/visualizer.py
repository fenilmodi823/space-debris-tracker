# visualizer.py
# Satellite visualization using Cartopy and Matplotlib (2D static + animated)

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from skyfield.api import load
import numpy as np
from utils import get_utc_timestamp

# -----------------------------------------
# Static Plot of Current Satellite Positions
# -----------------------------------------

def plot_positions(satellites, max_labels=10):
    """
    Plots current satellite positions on a 2D world map using Cartopy.

    Parameters:
        satellites (list): List of Skyfield EarthSatellite objects.
        max_labels (int): Max number of satellite names to annotate.
    """
    ts = load.timescale()
    t = ts.now()

    lats, lons, names = [], [], []

    for sat in satellites:
        try:
            subpoint = sat.at(t).subpoint()
            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees

            if not np.isnan(lat) and not np.isnan(lon):
                lats.append(lat)
                lons.append(lon)
                names.append(sat.name)
        except:
            continue

    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_global()

    ax.scatter(lons, lats, color='red', s=30, label='Satellites', zorder=5)

    for i in range(min(max_labels, len(names))):
        ax.text(lons[i] + 2, lats[i] + 2, names[i], fontsize=8, transform=ccrs.PlateCarree())

    plt.title("Satellite Positions – Earth View", fontsize=14)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.show()

# -----------------------------------------
# Animated Plot of Orbit Motion
# -----------------------------------------

def plot_animated_positions(satellites, steps=120, interval_ms=200):
    """
    Animates satellite positions on a rotating 2D Earth map.

    Parameters:
        satellites (list): List of Skyfield EarthSatellite objects.
        steps (int): Number of animation frames (time steps).
        interval_ms (int): Time between frames in milliseconds.
    """
    ts = load.timescale()
    t0 = ts.now()
    step_days = 1 / 86400  # 1 second in days
    time_steps = [t0 + i * step_days for i in range(steps)]

    sat_subset = satellites[:10]
    names = [sat.name for sat in sat_subset]
    all_tracks = []

    # Precompute position tracks
    for sat in sat_subset:
        track = []
        for t in time_steps:
            try:
                sp = sat.at(t).subpoint()
                lat = sp.latitude.degrees
                lon = ((sp.longitude.degrees + 180) % 360) - 180  # Wrap
                track.append((lat, lon))
            except:
                track.append((np.nan, np.nan))
        all_tracks.append(track)

    # Setup plot
    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_global()

    scat = ax.scatter([], [], color='red', s=25)
    labels = [ax.text(0, 0, '', fontsize=8, transform=ccrs.PlateCarree()) for _ in names]

    def update(frame):
        latlon = [all_tracks[i][frame] for i in range(len(sat_subset))]
        lats, lons = zip(*latlon)

        scat.set_offsets(np.c_[lons, lats])
        for i, label in enumerate(labels):
            label.set_position((lons[i] + 1, lats[i] + 1))
            label.set_text(names[i])

        ax.set_title(f"Satellite Animation – Frame {frame + 1} of {steps} | {get_utc_timestamp()}", fontsize=12)
        return scat, *labels

    ani = FuncAnimation(fig, update, frames=steps, interval=interval_ms, blit=True)
    plt.tight_layout()
    plt.show()
