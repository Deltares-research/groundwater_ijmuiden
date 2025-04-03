# plot thickness of clay layer in between phreatic and 1 aquifer as determined from the boreholes.

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Point

# %% open layers
metadata = pd.read_excel(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/01_metadata/peilbuizen_metadata.xlsx"
)
# metadata = metadata.set_index('Peilbuis')

geologie = pd.read_csv(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/04_boorgatmetingen/diepte_kleilagen_boorgatmetingen.csv",
    delimiter=";",
)

geologie = geologie.merge(
    metadata[["Peilbuis", "X-coord", "Y-coord"]], how="inner", on="Peilbuis"
)
geologie = geologie.set_index("Peilbuis")
geometry = [Point(xy) for xy in zip(geologie["X-coord"], geologie["Y-coord"])]
# metadata = metadata.drop(['X-coord', 'Y-coord'], axis=1)
gdf_geologie = gpd.GeoDataFrame(geologie, crs="EPSG:28992", geometry=geometry)

water = gpd.read_file(
    r"N:/Projects/11207500/11207510/F. Other information/gis-layers/Structuurvisie__Grote_wateren.shp"
)
water["color"] = [
    "skyblue",
    "lightblue",
    "lightblue",
    "lightblue",
    "lightblue",
    "lightblue",
]
land = gpd.read_file(
    r"N:/Projects/11207500/11207510/F. Other information/gis-layers/land.shp"
)

# %%
markersize = 10
textsize = 10
titlesize = 10


fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="darkblue", linewidth=0.3)
gdf_geologie.plot(ax=ax, c="black", markersize=markersize)
for idx, row in gdf_geologie.iterrows():
    if idx == "RWS-B26_2":
        ax.annotate(
            text=f"{np.round(row['eind freatische pakket'],2)} // {np.round(row['1e wvp']-row['eind freatische pakket'],2)}",
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(-50, 3),
            textcoords="offset points",
            size=textsize,
            color="black",
        )
    elif idx == "E_2":
        ax.annotate(
            text=f"{np.round(row['eind freatische pakket'],2)} // {np.round(row['1e wvp']-row['eind freatische pakket'],2)}",
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(-25, -11),
            textcoords="offset points",
            size=textsize,
            color="black",
        )

    else:
        ax.annotate(
            text=f"{np.round(row['eind freatische pakket'],2)} // {np.round(row['1e wvp']-row['eind freatische pakket'],2)}",
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(1, 3),
            textcoords="offset points",
            size=textsize,
            color="black",
        )

ax.set_ylim([497800, 499100])
ax.set_xlim([101000, 103500])
ax.set_axis_off()
ax.set_title(
    'Top (beneden 0 NAP, in m) en dikte (in m)"17 m-NAP kleilaag"',
    fontweight="bold",
    size=titlesize,
)
ax.text(
    102850,
    497900,
    "Noordzeekanaal",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax.text(
    101350,
    498000,
    "Noordzee",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
