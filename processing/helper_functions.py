import geopandas as gpd
import numpy as np

from matplotlib.lines import Line2D

MARKERSIZE = 10
TEXTSIZE = 8
TITLESIZE = 10


class ColorMap:
    aquifer_1 = "#255C99"
    aquifer_2 = "#B3001B"
    aquifer_3 = "#262626"


def rename_well(old: str):
    core = old.split("_")[0]

    if "Freatisch" in core:
        newname = core.replace(" - Freatisch", "_1")
    elif "Freat" in core:
        newname = core.replace(" - Freat", "_1")
    elif "WVP1" in core:
        if "B28" in core:
            core = core.replace("B28", "B27")
        newname = core.replace(" - WVP1", "_2")
    elif "WVP2" in core:
        if "B25A" in core:
            newname = core.replace(" - WVP2", "_3")
        else:
            newname = core.replace(" - WVP2", "_3")
    elif "TD" in core:
        newname = core.replace(" - TD-diver", "_TD")

    if "BL" in newname:
        newname = newname.replace("BL", "BL-")

    if "Z13PB600-02_2" == newname:
        newname = "Z13PB600_2"

    if "Z13PB600-02_1" == newname:
        newname = "Z13PB600_1"

    return newname


def plot_basemap(ax, add_legend=True):
    ax.set_ylim([497800, 499100])
    ax.set_xlim([101000, 103500])
    ax.set_axis_off()

    ax.text(
        102850,
        497920,
        "Noordzeekanaal",
        size=TEXTSIZE,
        color="darkslategrey",
        horizontalalignment="center",
    )
    ax.text(
        101350,
        498020,
        "Noordzee",
        size=TEXTSIZE,
        color="darkslategrey",
        horizontalalignment="center",
    )

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            label="freatisch pakket",
            markerfacecolor=ColorMap.aquifer_1,
            markersize=8,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            label="1e watervoerende pakket",
            markerfacecolor=ColorMap.aquifer_2,
            markersize=8,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            label="2e watervoerende pakket",
            markerfacecolor=ColorMap.aquifer_3,
            markersize=8,
        ),
    ]
    if add_legend:
        ax.legend(
            handles=legend_elements, loc="upper left", frameon=False, fontsize=TEXTSIZE
        )


def add_labels(
    ax,
    labels: gpd.GeoDataFrame,
    column: str,
    color: str | list = "black",
    xoffset: float = 0.0,
    yoffset: float = 4.0,
    textsize: float = 8,
):
    if isinstance(color, str):
        color = [color] * len(labels)

    for col, (label, row) in zip(color, labels.iterrows()):
        label = row[column]

        if isinstance(label, float):
            if np.isnan(label):
                continue
            else:
                label = f"{label:.2f}"

        elif isinstance(label, int):
            if label == 0:
                continue
            else:
                label = f"{label}"

        ax.annotate(
            text=label,
            xy=(row["X-coord"], row["Y-coord"]),
            xytext=(xoffset, yoffset),
            textcoords="offset points",
            size=textsize,
            color=col,
        )


def to_chloride_from(electrical_conductivity):
    """
    converts electrical conductivity [mS/cm] to chloride concentration [mg/L]
    """
    low_electrical_conductivity = 236 * electrical_conductivity - 146
    high_electrical_conductivity = 374 * electrical_conductivity - 423
    return np.where(
        electrical_conductivity < 2,
        low_electrical_conductivity,
        high_electrical_conductivity,
    )
