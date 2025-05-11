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
    Animates satellite positions with borders and labels using Cartopy.
    """
    ts = load.timescale()
    t0 = ts.now()
    time_steps = [t0 + i * 1 for i in range(120)]  # 2 minutes, 1s interval

    names = [sat.name for sat in satellites[:10]]
    positions = []

    for sat in satellites[:10]:
        track = []
        for t in time_steps:
            try:
                sp = sat.at(t).subpoint()
                lat = sp.latitude.degrees
                lon = sp.longitude.degrees
                lon_wrapped = (lon + 180) % 360 - 180
                track.append((lat, lon_wrapped))
            except:
                track.append((np.nan, np.nan))
        positions.append(track)

    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_global()

    scat = ax.scatter([], [], color='red', s=25)
    labels = [ax.text(0, 0, '', fontsize=8, transform=ccrs.PlateCarree()) for _ in names]

    def update(frame):
        lat_lon = [positions[i][frame] for i in range(len(positions))]
        lats, lons = zip(*lat_lon)
        scat.set_offsets(np.c_[lons, lats])
        for i, label in enumerate(labels):
            label.set_position((lons[i] + 1, lats[i] + 1))
            label.set_text(names[i])
        ax.set_title(f"Satellite Animation – Frame {frame+1} of {len(time_steps)}")
        return scat, *labels

    ani = FuncAnimation(fig, update, frames=len(time_steps), interval=200, blit=True)
    plt.show()
