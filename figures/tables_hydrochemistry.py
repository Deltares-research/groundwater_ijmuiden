# create table with hydrochemistry data for webviewer /05_waterkwaliteitmonsters/webviewer
from collections import OrderedDict

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def set_aquifer(peilbuis_id):
    aquifer = peilbuis_id.split("_")[-1]
    if aquifer == "1":
        return "Freatisch pakket"
    elif aquifer == "2":
        return "1e watervoerende pakket"
    elif aquifer == "3":
        return "2e watervoerende pakket"


path_monsters = r"N:/Projects/11207500/11207510/B. Measurements and calculations/05_waterkwaliteitmonsters/bemonstering_10-08-2022.xlsx"

excel = pd.read_excel(
    path_monsters,
    header=[0],
    index_col=0,
    skiprows=[1],
)
relevant_ions = [
    "Chloride",
    "Sulfate",
    "HCO3-",
    "Sodium",
    "Potassium",
    "Magnesium",
    "Calcium",
]

table = excel.loc[:, relevant_ions]  # excel.columns.isin(relevant_ions)
table = table.sort_index(ascending=True)
table.loc[:, "Pakket"] = table.index.map(set_aquifer).copy()
table.index.name = "Locatie"
table.index = table.index.map(lambda x: x.split("_")[0])
table = table.set_index("Pakket", append=True)
table = table.apply(pd.to_numeric, errors="coerce")

locations = [x[0] for x in table.index]
locations_np = []
[locations_np.append(element) for element in locations if element not in locations_np]

for location in locations_np:
    indices = [i for i in range(len(locations)) if locations[i] == location]
    order = np.arange(0, len(locations)).tolist()
    extracted_elements = []
    for i in reversed(indices):  # Loop through indices in reverse order
        extracted_elements.append(order.pop(i))
    for i in reversed(indices):
        order.insert(0, i)

    selection = table.iloc[order]

    fig, ax = plt.subplots(figsize=(12, 10))
    scaled = (selection - selection.min()) / (selection.max() - selection.min())
    ax = sns.heatmap(
        scaled, annot=selection, cbar=False, linewidths=0.5, fmt=".1f", cmap="Reds"
    )

    ylabel_mapping = OrderedDict()
    for locatie, pakket in selection.index:
        ylabel_mapping.setdefault(locatie, [])
        ylabel_mapping[locatie].append(pakket)

    xticks = [
        "$\\mathbf{Chloride}$ \n [mg/l]",
        "$\\mathbf{Sulfaat}$ \n [mg/l]",
        "$\\mathbf{HCO_{3}^{-}}$ \n [mg/l]",
        "$\\mathbf{Natrium}$ \n [mg/l]",
        "$\\mathbf{Kalium}$ \n [mg/l]",
        "$\\mathbf{Magnesium}$ \n [mg/l]",
        "$\\mathbf{Calcium}$ \n [mg/l]",
    ]
    hline = []
    new_ylabels = []
    for locatie, pakket_list in ylabel_mapping.items():
        if "watervoerend" in pakket_list[0]:
            pakket_list[0] = "{}  {}".format(
                "$\mathbf{" + locatie + "}$", pakket_list[0]
            )
            new_ylabels.extend(pakket_list)
        else:
            pakket_list[0] = "{}                {}".format(
                "$\mathbf{" + locatie + "}$", pakket_list[0]
            )
            new_ylabels.extend(pakket_list)

        if hline:
            hline.append(len(pakket_list) + hline[-1])
        else:
            hline.append(len(pakket_list))

    ax.hlines(hline[:-1], xmin=-2, xmax=7, color="black", linewidth=1)
    ax.set_yticklabels(new_ylabels)
    ax.set_xticklabels(xticks)
    ax.xaxis.tick_top()  # x axis on top
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("")
    ax.tick_params(left=False, bottom=False, top=False)
    plt.tight_layout()
    fig.savefig(
        f"N:/Projects/11207500/11207510/B. Measurements and calculations/05_waterkwaliteitmonsters/webviewer/{location}.png"
    )
    plt.close()


# %%
fig, ax = plt.subplots(figsize=(10, 3))
ax = sns.heatmap(
    table.loc["D"],
    annot=table.loc["D"],
    cbar=False,
    linewidths=0.5,
    fmt=".1f",
    cmap="Reds",
)
ax.set_yticklabels(new_ylabels[:2])
ax.set_xticklabels(xticks)
ax.xaxis.tick_top()  # x axis on top
ax.xaxis.set_label_position("top")
ax.set_ylabel("")
ax.tick_params(left=False, bottom=False, top=False)
plt.tight_layout()
