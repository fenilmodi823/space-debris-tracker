# visualizer.py
# Satellite visualization using Cartopy and Matplotlib (2D static + animated)

import warnings
warnings.filterwarnings("ignore", message=".*converting a masked element to nan.*")

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from itertools import count

from skyfield.api import load
from backend.utils import get_utc_timestamp, get_ml_satellite_color


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

    lats, lons, names, colors, labels_txt = [], [], [], [], []

    for sat in satellites:
        try:
            sp = sat.at(t).subpoint()
            lat = sp.latitude.degrees
            lon = sp.longitude.degrees
            if np.isnan(lat) or np.isnan(lon):
                continue

            lats.append(lat)
            lons.append(lon)
            names.append(sat.name)

            # ML color + optional label suffix
            c = get_ml_satellite_color(sat, fallback='red')
            colors.append(c)

            if hasattr(sat, "pred_type") and hasattr(sat, "pred_conf"):
                labels_txt.append(f"{sat.name} • {sat.pred_type} ({sat.pred_conf:.0%})")
            else:
                labels_txt.append(sat.name)
        except Exception:
            continue

    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_global()

    ax.scatter(lons, lats, color=colors, s=30, label='Satellites', zorder=5)

    for i in range(min(max_labels, len(names))):
        ax.text(lons[i] + 2, lats[i] + 2, labels_txt[i], fontsize=8, transform=ccrs.PlateCarree())

    plt.title("Satellite Positions – Earth View", fontsize=14)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.show()

# -----------------------------------------
# Animated Plot of Orbit Motion (finite)
# -----------------------------------------

def plot_animated_positions(satellites, steps=120, interval_ms=200, max_sats=10):
    """
    Animates satellite positions on a rotating 2D Earth map for a fixed number of frames.

    Parameters:
        satellites (list): List of Skyfield EarthSatellite objects.
        steps (int): Number of animation frames (time steps).
        interval_ms (int): Time between frames in milliseconds.
        max_sats (int): Max number of satellites to display.
    """
    ts = load.timescale()
    t0 = ts.now()
    step_days = 1 / 86400  # 1 second in days
    time_steps = [t0 + i * step_days for i in range(steps)]

    # Limit satellites for readability/perf
    sat_subset = satellites[:max_sats] if max_sats else satellites
    names = [sat.name for sat in sat_subset]

    # Precompute color per satellite (ML first, fallback red)
    colors = [get_ml_satellite_color(sat, fallback='red') for sat in sat_subset]

    # Precompute position tracks
    all_tracks = []
    for sat in sat_subset:
        track = []
        for t in time_steps:
            try:
                sp = sat.at(t).subpoint()
                lat = sp.latitude.degrees
                lon = ((sp.longitude.degrees + 180) % 360) - 180  # Wrap to [-180, +180]
                track.append((lat, lon))
            except Exception:
                track.append((np.nan, np.nan))
        all_tracks.append(track)

    # Setup plot
    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_global()

    # Initialize scatter with NaNs but correct number of points and per-point colors
    init_offsets = np.full((len(sat_subset), 2), np.nan)
    scat = ax.scatter(init_offsets[:, 1], init_offsets[:, 0], color=colors, s=25, zorder=5)

    # Prepare labels (include ML type if available)
    label_texts = [
        (f"{sat.name} • {sat.pred_type} ({sat.pred_conf:.0%})"
         if hasattr(sat, "pred_type") and hasattr(sat, "pred_conf")
         else sat.name)
        for sat in sat_subset
    ]
    labels = [ax.text(0, 0, '', fontsize=8, transform=ccrs.PlateCarree()) for _ in names]

    def update(frame):
        latlon = [all_tracks[i][frame] for i in range(len(sat_subset))]
        lats, lons = zip(*latlon)

        # Update scatter positions (note: scatter expects (x=lon, y=lat))
        scat.set_offsets(np.c_[lons, lats])

        # Update label positions/text
        for i, label in enumerate(labels):
            label.set_position((lons[i] + 1, lats[i] + 1))
            label.set_text(label_texts[i])

        ax.set_title(
            f"Satellite Animation – Frame {frame + 1} of {steps} | {get_utc_timestamp()}",
            fontsize=12
        )
        return scat, *labels

    ani = FuncAnimation(fig, update, frames=steps, interval=interval_ms, blit=True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------
# Animated Plot of Orbit Motion (live, infinite)
# -----------------------------------------

def plot_animated_positions_live(satellites, interval_ms=200, max_sats=50):
    """
    Live animation: updates continuously until the window is closed.
    It recomputes positions at 'now' each frame (no fixed-length precompute).

    Parameters:
        satellites (list): List of Skyfield EarthSatellite objects.
        interval_ms (int): Time between frames in milliseconds.
        max_sats (int): Max number of satellites to display (None for all).
    """
    ts = load.timescale()
    sat_subset = satellites[:max_sats] if max_sats else satellites
    names = [sat.name for sat in sat_subset]

    # Precompute colors (constant per satellite)
    colors = [get_ml_satellite_color(sat, fallback='red') for sat in sat_subset]

    # Setup plot
    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_global()

    # Initialize scatter with NaNs but correct number of points and per-point colors
    init_offsets = np.full((len(sat_subset), 2), np.nan)
    scat = ax.scatter(init_offsets[:, 1], init_offsets[:, 0], color=colors, s=25, zorder=5)

    # Prepare labels (include ML type if available)
    label_texts = [
        (f"{sat.name} • {sat.pred_type} ({sat.pred_conf:.0%})"
         if hasattr(sat, "pred_type") and hasattr(sat, "pred_conf")
         else sat.name)
        for sat in sat_subset
    ]
    labels = [ax.text(0, 0, '', fontsize=8, transform=ccrs.PlateCarree()) for _ in names]

    def _frame_gen():
        # Infinite generator: yields 0,1,2,... forever
        for i in count():
            yield i

    def _update(_):
        t = ts.now()
        lats, lons = [], []
        for sat in sat_subset:
            try:
                sp = sat.at(t).subpoint()
                lat = sp.latitude.degrees
                lon = ((sp.longitude.degrees + 180) % 360) - 180  # wrap
                if np.isnan(lat) or np.isnan(lon):
                    lats.append(np.nan); lons.append(np.nan)
                else:
                    lats.append(lat); lons.append(lon)
            except Exception:
                lats.append(np.nan); lons.append(np.nan)

        # Update scatter positions
        scat.set_offsets(np.c_[lons, lats])

        # Update labels
        for i, label in enumerate(labels):
            label.set_position((lons[i] + 1, lats[i] + 1))
            label.set_text(label_texts[i])

        ax.set_title(f"Satellite Live Animation | {get_utc_timestamp()}", fontsize=12)
        return scat, *labels

    ani = FuncAnimation(fig, _update, frames=_frame_gen, interval=interval_ms, blit=True)
    plt.tight_layout()
    plt.show()
