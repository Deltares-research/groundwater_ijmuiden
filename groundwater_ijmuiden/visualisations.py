import matplotlib.pyplot as plt
import pandas as pd
from .diver_processing import MonitoringWell


def plot_groundwater(monitoring_well: MonitoringWell, freq: str = "1D"):
    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        dpi=400,
        figsize=(8.27, 11.69 / 3),
        sharey=True,
        sharex=True,
    )
    monitoring_well.gw_measurements.plot(ax=ax, color="red", style=".")

    monitoring_well.point_water_head.groupby(pd.Grouper(freq=freq)).mean().plot(
        ax=ax, color="black", lw=0.4
    )
    monitoring_well.fresh_water_head.groupby(pd.Grouper(freq=freq)).mean().plot(
        ax=ax, color="darkblue", lw=0.4
    )
    monitoring_well.fresh_water_ref_head.groupby(pd.Grouper(freq=freq)).mean().plot(
        ax=ax, color="darkgreen", lw=0.4
    )
    ax.set_ylim(-1.2, 1.2)
    ax.set_ylabel("(m NAP)")
    plt.legend(frameon=False, fontsize=8)
    ax.set_title(monitoring_well.well_id)

    return fig
