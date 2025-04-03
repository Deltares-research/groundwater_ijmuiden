import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from shapely.geometry import Point

# %%
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

names = ["A", "RWS-B26", "C", "E"]
fig, axs = plt.subplots(
    nrows=1, ncols=4, dpi=400, figsize=(26, 11.69 / 2.5), sharey=True, sharex=True
)

for ax, name in zip(axs.ravel(), names):
    fp = pd.read_csv(
        f"N:/Projects/11207500/11207510/B. Measurements and calculations/03_divers/zoetwaterstijghoogte/{name}_1.csv",
        index_col=0,
        parse_dates=[0],
    )
    wvp1 = pd.read_csv(
        f"N:/Projects/11207500/11207510/B. Measurements and calculations/03_divers/zoetwaterstijghoogte/{name}_2.csv",
        index_col=0,
        parse_dates=[0],
    )

    try:
        wvp2 = pd.read_csv(
            f"N:/Projects/11207500/11207510/B. Measurements and calculations/03_divers/zoetwaterstijghoogte/{name}_3.csv",
            index_col=0,
            parse_dates=[0],
        )

        fp.resample("D").mean().plot(ax=ax, color="black")
        wvp1.resample("D").mean().plot(ax=ax, color="maroon")
        wvp2.resample("D").mean().plot(ax=ax, color="navy")
        legend_handles = [
            Line2D([0], [0], color="black", label="Freatisch pakket"),
            Line2D([0], [0], color="maroon", label="1e watervoerende pakket"),
            Line2D([0], [0], color="navy", label="2e watervoerende pakket"),
        ]

        ax.legend(handles=legend_handles, frameon=False)
        ax.set_ylim([-1.25, 1.25])
        ax.set_ylabel("Zoetwaterstijghoogte (m NAP)")
        ax.set_xlabel("")
        ax.set_xlim(["2022-07-18", "2023-05-9"])
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)

    except FileNotFoundError:

        fp.resample("D").mean().plot(ax=ax, color="black")
        wvp1.resample("D").mean().plot(ax=ax, color="maroon")
        legend_handles = [
            Line2D([0], [0], color="black", label="Freatisch pakket"),
            Line2D([0], [0], color="maroon", label="1e watervoerende pakket"),
        ]

        # Add legend with custom handles
        ax.legend(handles=legend_handles, frameon=False)
        ax.set_ylim([-1.25, 1.25])
        ax.set_ylabel("Zoetwaterstijghoogte (m NAP)", fontsize=14)
        ax.set_xlabel("")
        ax.set_xlim(["2022-07-18", "2024-12-1"])
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
fig.tight_layout(pad=0.0)

# %% Plot
metadata = pd.read_excel(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/01_metadata/peilbuizen_metadata.xlsx"
)
geometry = [Point(xy) for xy in zip(metadata["X-coord"], metadata["Y-coord"])]
# metadata = metadata.drop(['X-coord', 'Y-coord'], axis=1)
gdf = gpd.GeoDataFrame(metadata, crs="EPSG:28992", geometry=geometry).set_index(
    "Peilbuis"
)
for i, row in gdf.iterrows():
    name = i

    if name in [
        "B25A0942_3_extra",
        "B25A0942_5_extra",
        "B25A0942_6_extra",
        "B25A0942_7_extra",
        "Z13PB600_1_extra",
        "D_2",
        "RWS-04-1_1",
        "RWS-04-4_2",
    ]:
        continue
    else:
        data = pd.read_csv(
            f"N:/Projects/11207500/11207510/B. Measurements and calculations/03_divers/zoetwaterstijghoogte/{name}.csv"
        )
        gdf.loc[i, "fwh"] = data["fresh_water_head (m NAP)"].mean()


markersize = 10
textsize = 10
titlesize = 12

gdf = gdf.reset_index()
notnan = ~np.isnan(gdf.fwh)
aquifer_1 = gdf["Peilbuis"].str.contains("_1") * notnan
aquifer_2 = gdf["Peilbuis"].str.contains("_2") * notnan
aquifer_3 = (
    (gdf["Peilbuis"].str.contains("_3")) | (gdf["Peilbuis"].str.contains("_4"))
) * notnan

# grondwaterstand
fig, ax = plt.subplots(
    nrows=3, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax[0], color="lightgrey")
water.plot(ax=ax[0], color=water.color, edgecolor="darkblue", linewidth=0.3)
gdf[aquifer_1][["Peilbuis", "geometry"]].plot(
    ax=ax[0], c="black", markersize=markersize
)
for idx, row in gdf[aquifer_1].iterrows():
    ax[0].annotate(
        text=np.round(row["fwh"], 2),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, 1),
        textcoords="offset points",
        size=textsize,
    )
ax[0].set_ylim([497800, 499100])
ax[0].set_xlim([101000, 103500])
ax[0].set_axis_off()
ax[0].set_title("Freatisch pakket", size=titlesize)
ax[0].text(
    102850,
    497900,
    "Noordzeekanaal \n (ca. -0.4 [m NAP])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax[0].text(
    101350,
    498000,
    "Noordzee \n (-1.35 - 1.80 [m NAP])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)

land.plot(ax=ax[1], color="lightgrey")
water.plot(ax=ax[1], color=water.color, edgecolor="darkblue", linewidth=0.3)
gdf[aquifer_2][["Peilbuis", "geometry"]].plot(
    ax=ax[1], c="black", markersize=markersize
)
for idx, row in gdf[aquifer_2].iterrows():
    ax[1].annotate(
        text=np.round(row["fwh"], 2),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, 1),
        textcoords="offset points",
        size=textsize,
    )
ax[1].set_ylim([497800, 499100])
ax[1].set_xlim([101000, 103500])
ax[1].set_axis_off()
ax[1].set_title("1e watervoerende pakket", size=titlesize)

land.plot(ax=ax[2], color="lightgrey")
water.plot(ax=ax[2], color=water.color, edgecolor="darkblue", linewidth=0.3)
gdf[aquifer_3][["Peilbuis", "geometry"]].plot(
    ax=ax[2], c="black", markersize=markersize
)
for idx, row in gdf[aquifer_3].iterrows():
    ax[2].annotate(
        text=np.round(row["fwh"], 2),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, 1),
        textcoords="offset points",
        size=textsize,
    )
ax[2].set_ylim([497800, 499100])
ax[2].set_xlim([101000, 103500])
ax[2].set_axis_off()
ax[2].set_title("2e watervoerende pakket", size=titlesize)

fig.tight_layout()
fig.subplots_adjust(top=0.93)
fig.suptitle("Stijghoogte [m NAP]", fontweight="bold", size=12)

#

# %% grondwaterstand
markersize = 10
textsize = 9
titlesize = 10

fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="darkblue", linewidth=0.3)
gdf[~np.isnan(gdf.fwh)][["Peilbuis", "geometry"]].plot(
    ax=ax, c="black", markersize=markersize
)
for idx, row in gdf[aquifer_1].iterrows():
    ax.annotate(
        text=np.round(row["fwh"], 2),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, 3),
        textcoords="offset points",
        size=textsize,
        color="black",
    )

for idx, row in gdf[aquifer_2].iterrows():
    ax.annotate(
        text=np.round(row["fwh"], 2),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, -7),
        textcoords="offset points",
        size=textsize,
        color="maroon",
    )

for idx, row in gdf[aquifer_3].iterrows():
    ax.annotate(
        text=np.round(row["fwh"], 2),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, -16),
        textcoords="offset points",
        size=textsize,
        color="navy",
    )

ax.annotate(text="x.xx: freatisch pakket", xy=(101020, 499050), size=8, color="black")
ax.annotate(
    text="x.xx: 1e watervoerende pakket", xy=(101020, 498990), size=8, color="maroon"
)
ax.annotate(
    text="x.xx: 2e watervoerende pakket", xy=(101020, 498925), size=8, color="navy"
)

ax.set_ylim([497800, 499100])
ax.set_xlim([101000, 103500])
ax.set_axis_off()
ax.set_title("Stijghoogte [m NAP]", fontweight="bold", size=titlesize)
ax.text(
    102850,
    497900,
    "Noordzeekanaal \n (ca. -0.4 [m NAP])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax.text(
    101350,
    498000,
    "Noordzee \n (-1.35 - 1.80 [m NAP])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
