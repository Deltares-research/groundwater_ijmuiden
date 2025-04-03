# %%
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import groundwater_ijmuiden as gij

from shapely.geometry import Point
from pathlib import Path
from helper_functions import plot_basemap, ColorMap, add_labels, to_chloride_from

MARKERSIZE = 10
TEXTSIZE = 8
TITLESIZE = 10


project_dir = Path(r"N:/Projects/11207500/11207510")
data_dir = project_dir.joinpath("B. Measurements and calculations")
gis_dir = project_dir.joinpath("F. Other information", "gis-layers")
diver_dir = data_dir.joinpath("03_divers", "zoetwaterstijghoogte")
measurements_dir = data_dir.joinpath("02_handmetingen")

path_metadata = data_dir.joinpath("01_metadata", "peilbuizen_metadata.xlsx")
path_layer_land = gis_dir.joinpath("land.shp")
path_layer_water = gis_dir.joinpath("Structuurvisie__Grote_wateren.shp")

# open metadata
metadata = pd.read_excel(path_metadata, index_col=0)
geometry = [Point(xy) for xy in zip(metadata["X-coord"], metadata["Y-coord"])]
metadata = gpd.GeoDataFrame(metadata, crs="EPSG:28992", geometry=geometry)
valid_wells = ~metadata.index.str.contains("_extra")

# open gis layers
water = gpd.read_file(path_layer_water)
water["color"] = [
    "skyblue",
    "lightblue",
    "lightblue",
    "lightblue",
    "lightblue",
    "lightblue",
]
land = gpd.read_file(path_layer_land)

#
mask_aquifer_1 = metadata.index.str.contains("_1") & valid_wells
mask_aquifer_2 = metadata.index.str.contains("_2") & valid_wells
mask_aquifer_2_active = mask_aquifer_2 & (metadata.index != "Z13PB600_2")
mask_aquifer_3 = metadata.index.str.contains("_3") & valid_wells

# %% overview map
# location labels
metadata["location"] = metadata.index.str.split("_").str[0]
labels = metadata[["X-coord", "Y-coord", "location"]].groupby("location").mean()

fig, ax = plt.subplots(dpi=400, figsize=(8.27, 11.69))
# background layers
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="black", linewidth=0.3)
# monitoring wells
metadata[mask_aquifer_1].plot(ax=ax, color=ColorMap.aquifer_1, markersize=60)
metadata[mask_aquifer_2_active].plot(ax=ax, color=ColorMap.aquifer_2, markersize=30)
metadata[mask_aquifer_3].plot(ax=ax, color=ColorMap.aquifer_3, markersize=8)

# add labels
add_labels(ax, labels.reset_index(), column="location", textsize=7)
# plot basemap
plot_basemap(ax=ax)
ax.set_title("Status meetnet IJmuiden", fontweight="bold", size=TITLESIZE)

# %% plot mean groundwater level

well_ids = metadata.index.to_list()
for well_id in well_ids:
    path_head = diver_dir.joinpath(f"{well_id}.csv")
    try:
        head = pd.read_csv(path_head, index_col=0, parse_dates=True)
    except FileNotFoundError:
        continue
    metadata.loc[well_id, "mean_gw"] = head["fresh_water_head (m NAP)"].mean().item()
    metadata.loc[well_id, "mean_2023"] = (
        head["fresh_water_head (m NAP)"].loc["2023-01-01":"2023-12-31"].mean()
    )
    metadata.loc[well_id, "mean_2024"] = (
        head["fresh_water_head (m NAP)"].loc["2024-01-01":"2024-12-31"].mean()
    )
metadata["difference"] = metadata["mean_2024"] - metadata["mean_2023"]
(
    metadata[mask_aquifer_1]["mean_2024"].mean()
    - metadata[mask_aquifer_2]["mean_2024"].mean()
)
(
    metadata[mask_aquifer_1]["mean_2023"].mean()
    - metadata[mask_aquifer_2]["mean_2023"].mean()
)

# %%
fig, ax = plt.subplots(dpi=400, figsize=(8.27, 11.69))
# background layers
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="black", linewidth=0.3)
# monitoring wells

metadata.plot(ax=ax, color="black", markersize=20)

add_labels(
    ax=ax,
    labels=metadata[mask_aquifer_1],
    column="mean_gw",
    color=ColorMap.aquifer_1,
    xoffset=3,
    yoffset=7,
)

add_labels(
    ax=ax,
    labels=metadata[mask_aquifer_2],
    column="mean_gw",
    color=ColorMap.aquifer_2,
    xoffset=3,
    yoffset=0,
)

add_labels(
    ax=ax,
    labels=metadata[mask_aquifer_3],
    column="mean_gw",
    color=ColorMap.aquifer_3,
    xoffset=3,
    yoffset=-7,
)
# plot basemap
plot_basemap(ax=ax)
ax.set_title("Zoetwaterstijghoogte (in m NAP)", fontweight="bold", size=TITLESIZE)

# %%

campaign_dates = [
    "18052022",
    "09082022",
    "07022023",
    "23052023",
    "19092023",
    "23012024",
    "10042024",
    "22052024",
    "02122024",
]
chloride = pd.DataFrame()
for date in campaign_dates:
    path = measurements_dir.joinpath(f"handmetingen_{date}.csv")

    df = gij.readers.read_ec_measurement(path)
    # date = pd.to_datetime(date, format="%d%m%Y")

    chloride[date] = df.apply(to_chloride_from)

start = ["09082022", "07022023", "23052023"]
eind = ["23012024", "10042024", "22052024", "02122024"]
start_d2 = ["07022023", "23052023", "19092023"]
chloride["increase"] = chloride.loc[:, eind].mean(axis=1, skipna=True) - chloride.loc[
    :, start
].mean(axis=1, skipna=True)
chloride.loc["D_2", "increase"] = (
    chloride.loc["D_2", eind].mean() - chloride.loc["D_2", start_d2].mean()
)
chloride["mean_cl"] = chloride.iloc[:, :7].mean(axis=1, skipna=True)


# %%----------------------------------------------------------------

chloride = metadata.join(chloride["mean_cl"].fillna(0).astype(int))

fig, ax = plt.subplots(dpi=400, figsize=(8.27, 11.69))
# background layers
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="black", linewidth=0.3)
# monitoring wells
chloride.plot(ax=ax, color="black", markersize=10)

add_labels(
    ax=ax,
    labels=chloride[mask_aquifer_1],
    column="mean_cl",
    color=ColorMap.aquifer_1,
    xoffset=3,
    yoffset=7,
)

add_labels(
    ax=ax,
    labels=chloride[mask_aquifer_2],
    column="mean_cl",
    color=ColorMap.aquifer_2,
    xoffset=3,
    yoffset=0,
)

add_labels(
    ax=ax,
    labels=chloride[mask_aquifer_3],
    column="mean_cl",
    color=ColorMap.aquifer_3,
    xoffset=3,
    yoffset=-7,
)
# plot basemap
plot_basemap(ax=ax)

ax.text(
    102850,
    497900 - 20,
    "(5814 mg Cl/L)",
    size=TEXTSIZE,
    color="darkslategrey",
    horizontalalignment="center",
)
ax.text(
    101350,
    498000 - 20,
    "(12584 mg Cl/L)",
    size=TEXTSIZE,
    color="darkslategrey",
    horizontalalignment="center",
)

ax.set_title(
    "Geschatte chlorideconcentratie (in mg/L)", fontweight="bold", size=TITLESIZE
)


# %%
to_plot = metadata.join(chloride["increase"])
to_plot["increase"] = to_plot["increase"].fillna(0).astype(int)
fig, ax = plt.subplots(dpi=400, figsize=(8.27, 11.69))
# background layers
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="black", linewidth=0.3)
# ecs
to_plot[mask_aquifer_2].plot(ax=ax, color="black", markersize=15)
add_labels(
    ax=ax,
    labels=to_plot[mask_aquifer_2],
    column="increase",
    color=np.where(
        to_plot[mask_aquifer_2]["increase"] > 0, ColorMap.aquifer_2, ColorMap.aquifer_1
    ),
    xoffset=3,
    yoffset=0,
)
plot_basemap(ax, add_legend=False)
ax.set_title(
    "Verschil chlorideconcentratie (in mg/L) in 1e watervoerende pakket",
    fontweight="bold",
    size=TITLESIZE,
)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

aquifer_2_chloride = chloride.iloc[:, :-2].loc[["C_3", "B25A0942_3"]]
date = pd.to_datetime(aquifer_2_chloride.columns, format="%d%m%Y")
aquifer_2_chloride.columns = date


fig, ax = plt.subplots(dpi=400, figsize=(8.27, 11.69 / 2))
aquifer_2_chloride.loc["C_3"].T.plot(
    ax=ax, kind="line", style=".", color="red", label="C"
)
aquifer_2_chloride.loc["B25A0942_3"].T.plot(
    ax=ax, kind="line", style="x", color="black", label="B25A0942"
)
ax.set_ylabel("Chlorideconcentratie (mg/L)")
ax.set_title("Chlorideconcentratie in 2e watervoerende pakket", fontweight="bold")
ax.set_xlabel("")
ax.legend()

# %%


for idx, row in label.iterrows():
    if row.Peilbuis in ["RWS-B26", "RWS-04-1", "RWS-04-2"]:
        ax.annotate(
            text=row["Peilbuis"],
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(-40, 3),
            textcoords="offset points",
            size=textsize,
            color="black",
        )
    else:
        ax.annotate(
            text=row["Peilbuis"],
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(1, 3),
            textcoords="offset points",
            size=textsize,
            color="black",
        )

plt.legend(
    ["2e watervoerende pakket", "1e watervoerende pakket", "freatisch pakket"],
    frameon=False,
    fontsize=8,
    loc="upper left",
)

# ax.annotate(text='x.xx: freatisch pakket', xy=(101020,499050), size = 8,color = 'black')
# ax.annotate(text='x.xx: 1e watervoerende pakket', xy=(101020,498990), size = 8,color = 'maroon')
# ax.annotate(text='x.xx: 2e watervoerende pakket', xy=(101020,498925), size = 8,color = 'navy')


handmetingen = pd.read_csv(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/02_handmetingen/handmetingen_23052023.csv",
    skiprows=19,
    delimiter=";",
    encoding="ISO-8859-1",
    index_col=0,
)


bemonstering = pd.read_excel(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/05_waterkwaliteitmonsters/bemonstering_10-08-2022.xlsx",
    header=0,
)
bemonstering = bemonstering.drop(index=0).set_index("Peilbuis")
bemonstering = bemonstering.replace("n.a.", np.nan)
bemonstering.columns = bemonstering.columns.str.replace("\n \n", "")
bemonstering.columns = bemonstering.columns.str.replace("\n", "")

# %% groundwater
grw = gdf.copy()
for i, row in grw.iterrows():
    name = row.Peilbuis

    if name in [
        "B25A0942_3_extra",
        "B25A0942_5_extra",
        "B25A0942_6_extra",
        "B25A0942_7_extra",
        "Z13PB600_1_extra",
        "D_2",
    ]:
        continue
    else:
        grw.loc[i, "ec"] = handmetingen.loc[name, "Electrical Conductivity[ÂµS/cm]"]
        grw.loc[i, "cl"] = bemonstering.loc[name, "Chloride"]
        grw.loc[i, "Ca/HCO3-"] = (bemonstering.loc[name, "Calcium"] * 2 / 40.078) / (
            bemonstering.loc[name, "HCO3-"] / 61.01688
        )


x = grw.sort_values("ec").loc[:, "ec"].values
y = grw.sort_values("ec").loc[:, "cl"].values
nans = np.isnan(x) | np.isnan(y)
length = len(x[~nans])
x = x[~nans].reshape(length, 1)
y = y[~nans].reshape(length, 1)
reg = LinearRegression().fit(x, y)
reg.coef_
reg.intercept_
# %%
fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69 / 3), sharey=True, sharex=True
)
grw.plot.scatter("ec", "cl", ax=ax, color="red")
ax.plot(x, reg.predict(x), color="blue", linewidth=2, ls="--")
ax.set_xlabel("EC [mS/cm]")
ax.set_ylabel("Chloride [mg/L]")
ax.set_yscale("log")

ax.hlines(150, 0, 40, color="black")
ax.hlines(300, 0, 40, color="black")
ax.hlines(1000, 0, 40, color="black")
ax.hlines(10000, 0, 40, color="black")
ax.annotate(text="zoet", xy=(35, 60))
ax.annotate(text="zoet-\nbrak", xy=(35, 170))
ax.annotate(text="brak", xy=(35, 470))
ax.annotate(text="brak-zout", xy=(35, 2200))
ax.annotate(text="zout", xy=(35, 12000))
ax.set_xlim([0, 40])
ax.set_ylim([0, 20000])
ax.set_title("Relatie EC en Chloride-concentratie", fontweight="bold", size=10)
# %%
markersize = 10
textsize = 10
titlesize = 12

aquifer_1 = grw["Peilbuis"].str.contains("_1")
aquifer_2 = grw["Peilbuis"].str.contains("_2")
aquifer_3 = (grw["Peilbuis"].str.contains("_3")) | (grw["Peilbuis"].str.contains("_4"))

fig, ax = plt.subplots(
    nrows=3, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax[0], color="lightgrey")
water.plot(ax=ax[0], color=water.color, edgecolor="darkblue", linewidth=0.3)
grw[aquifer_1][["Peilbuis", "geometry"]].plot(
    ax=ax[0], c="black", markersize=markersize
)
for idx, row in grw[aquifer_1].iterrows():
    ax[0].annotate(
        text=np.round(row["ec"]),
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
    "Noordzeekanaal \n (16700 [µS/cm])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax[0].text(
    101350,
    498000,
    "Noordzee \n (34500 [µS/cm])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)

land.plot(ax=ax[1], color="lightgrey")
water.plot(ax=ax[1], color=water.color, edgecolor="darkblue", linewidth=0.3)
grw[aquifer_2][["Peilbuis", "geometry"]].plot(
    ax=ax[1], c="black", markersize=markersize
)
for idx, row in grw[aquifer_2].iterrows():
    ax[1].annotate(
        text=np.round(row["ec"]),
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
grw[aquifer_3][["Peilbuis", "geometry"]].plot(
    ax=ax[2], c="black", markersize=markersize
)
for idx, row in grw[aquifer_3].iterrows():
    ax[2].annotate(
        text=np.round(row["ec"]),
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
fig.suptitle("Electrical Conductivity [µS/cm]", fontweight="bold", size=12)

# %%
markersize = 10
textsize = 9
titlesize = 10

valid = (~np.isnan(grw.cl)) & (~(grw["Peilbuis"] == "Z13PB600-02_1"))
aquifer_1 = grw["Peilbuis"].str.contains("_1") * valid
aquifer_2 = grw["Peilbuis"].str.contains("_2") * valid
aquifer_3 = (
    (grw["Peilbuis"].str.contains("_3")) | (grw["Peilbuis"].str.contains("_4"))
) * valid


fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="darkblue", linewidth=0.3)
grw[~np.isnan(grw["Ca/HCO3-"])][["Peilbuis", "geometry"]].plot(
    ax=ax, c="black", markersize=markersize
)
for idx, row in grw[aquifer_1].iterrows():
    ax.annotate(
        text=str(np.round(row["Ca/HCO3-"], 2)),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, 3),
        textcoords="offset points",
        size=textsize,
        color="black",
    )

for idx, row in grw[aquifer_2].iterrows():
    ax.annotate(
        text=str(np.round(row["Ca/HCO3-"], 2)),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, -7),
        textcoords="offset points",
        size=textsize,
        color="maroon",
    )

for idx, row in grw[aquifer_3].iterrows():
    ax.annotate(
        text=str(np.round(row["Ca/HCO3-"], 2)),
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
ax.set_title("Calcium Bicarbonaat-ratio", fontweight="bold", size=10)
ax.text(
    102850,
    497900,
    f"Noordzeekanaal",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax.text(
    101350,
    498000,
    f"Noordzee",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)

# %% calcium/hco3 ratio
markersize = 10
textsize = 9
titlesize = 10

valid = (~np.isnan(grw.cl)) & (~(grw["Peilbuis"] == "Z13PB600-02_1"))
aquifer_1 = grw["Peilbuis"].str.contains("_1") * valid
aquifer_2 = grw["Peilbuis"].str.contains("_2") * valid
aquifer_3 = (
    (grw["Peilbuis"].str.contains("_3")) | (grw["Peilbuis"].str.contains("_4"))
) * valid


fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="darkblue", linewidth=0.3)
grw[~np.isnan(grw["cl"])][["Peilbuis", "geometry"]].plot(
    ax=ax, c="black", markersize=markersize
)
for idx, row in grw[aquifer_1].iterrows():
    ax.annotate(
        text=str(np.round(row["cl"])),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, 3),
        textcoords="offset points",
        size=textsize,
        color="black",
    )

for idx, row in grw[aquifer_2].iterrows():
    ax.annotate(
        text=str(np.round(row["cl"], 2)),
        xy=(row["geometry"].x, row["geometry"].y),
        xytext=(1, -7),
        textcoords="offset points",
        size=textsize,
        color="maroon",
    )

for idx, row in grw[aquifer_3].iterrows():
    ax.annotate(
        text=str(np.round(row["cl"], 2)),
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
ax.set_title("Chloride-concentratie [mg/L]", fontweight="bold", size=10)
ax.text(
    102850,
    497900,
    f"Noordzeekanaal \n ({int(reg.predict(np.array([16.7]).reshape(1,1))[0][0])} [mg/L])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax.text(
    101350,
    498000,
    f"Noordzee \n ({int(reg.predict(np.array([34.5]).reshape(1,1))[0][0])} [mg/L])",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)

# %%
markersize = 10
textsize = 8
titlesize = 10

valid = ~(grw["Peilbuis"] == "Z13PB600-02_1")
aquifer_1 = grw["Peilbuis"].str.contains("_1") * valid
aquifer_2 = grw["Peilbuis"].str.contains("_2") * valid
aquifer_3 = (
    (grw["Peilbuis"].str.contains("_3")) | (grw["Peilbuis"].str.contains("_4"))
) * valid

label = grw.copy()
labels = []
for i, row in label.iterrows():
    labels.append(row.Peilbuis.split("_")[0])
label["Peilbuis"] = labels
label = label.drop_duplicates(subset="Peilbuis").drop(index=[35, 36])

fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69), sharey=True, sharex=True
)
land.plot(ax=ax, color="lightgrey")
water.plot(ax=ax, color=water.color, edgecolor="darkblue", linewidth=0.3)
grw[aquifer_3][["Peilbuis", "geometry"]].plot(ax=ax, color="navy", markersize=60)
grw[aquifer_2][["Peilbuis", "geometry"]].plot(ax=ax, color="maroon", markersize=30)
grw[aquifer_1][["Peilbuis", "geometry"]].plot(ax=ax, color="black", markersize=10)


for idx, row in label.iterrows():
    if row.Peilbuis in ["RWS-B26", "RWS-04-1", "RWS-04-2"]:
        ax.annotate(
            text=row["Peilbuis"],
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(-40, 3),
            textcoords="offset points",
            size=textsize,
            color="black",
        )
    else:
        ax.annotate(
            text=row["Peilbuis"],
            xy=(row["geometry"].x, row["geometry"].y),
            xytext=(1, 3),
            textcoords="offset points",
            size=textsize,
            color="black",
        )

plt.legend(
    ["2e watervoerende pakket", "1e watervoerende pakket", "freatisch pakket"],
    frameon=False,
    fontsize=8,
    loc="upper left",
)

# ax.annotate(text='x.xx: freatisch pakket', xy=(101020,499050), size = 8,color = 'black')
# ax.annotate(text='x.xx: 1e watervoerende pakket', xy=(101020,498990), size = 8,color = 'maroon')
# ax.annotate(text='x.xx: 2e watervoerende pakket', xy=(101020,498925), size = 8,color = 'navy')

ax.set_ylim([497800, 499100])
ax.set_xlim([101000, 103500])
ax.set_axis_off()
ax.set_title("Gerealiseerd meetnetwerk", fontweight="bold", size=10)
ax.text(
    102850,
    497900,
    f"Noordzeekanaal",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)
ax.text(
    101350,
    498000,
    f"Noordzee",
    size=textsize,
    color="darkslategrey",
    horizontalalignment="center",
)


# %%
