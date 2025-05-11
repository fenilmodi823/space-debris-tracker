import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from skyfield.api import load
import numpy as np

def plot_positions(satellites):
    """
    Plots the positions of satellites on a 2D world map using Cartopy.
    """
    ts = load.timescale()
    t = ts.now()

    lats, lons, names = [], [], []

    for sat in satellites:
        try:
            geocentric = sat.at(t)
            subpoint = geocentric.subpoint()
            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees

            if not (lat != lat or lon != lon):
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

    for i in range(min(10, len(names))):
        ax.text(lons[i] + 2, lats[i] + 2, names[i], fontsize=8, transform=ccrs.PlateCarree())

    plt.title("Satellite Positions – Earth View", fontsize=14)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.show()

def plot_animated_positions(satellites):
    """
    Animates the positions of satellites over time on a 2D world map.
    """
    ts = load.timescale()
    t0 = ts.now()
    time_steps = [t0 + i * 30 for i in range(60)]  # 30 minutes, 30s interval

    positions = []
    for sat in satellites[:10]:  # Limit to 10 satellites
        track = []
        for t in time_steps:
            try:
                sp = sat.at(t).subpoint()
                track.append((sp.latitude.degrees, sp.longitude.degrees))
            except:
                track.append((np.nan, np.nan))
        positions.append(track)

    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.set_global()

    scat = ax.scatter([], [], color='red', s=25)

    def update(frame):
        lat_lon = [positions[i][frame] for i in range(len(positions))]
        lats, lons = zip(*lat_lon)
        scat.set_offsets(np.c_[lons, lats])
        ax.set_title(f"Satellite Animation – Frame {frame+1} of {len(time_steps)}")
        return scat,

    ani = FuncAnimation(fig, update, frames=len(time_steps), interval=150, blit=True)
    plt.show()
