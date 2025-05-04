import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from skyfield.api import load

def plot_positions(satellites):
    """
    Plots the positions of satellites on a 2D world map using Cartopy.
    """
    ts = load.timescale()
    t = ts.now()

    lats = []
    lons = []
    names = []

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

    # Plotting with Cartopy
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()

    plt.scatter(lons, lats, color='red', s=20)

    for i in range(min(10, len(names))):
        plt.text(lons[i], lats[i], names[i], fontsize=8, transform=ccrs.PlateCarree())

    plt.title("Satellite Positions (2D World Map)")
    plt.show()
