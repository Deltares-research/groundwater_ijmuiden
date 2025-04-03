from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mendeleev import element

plt.rcParams["font.family"] = "Calibri"

basedir = Path(r"N:/Projects/11207500/11207510/B. Measurements and calculations")
path_metadata = basedir / "01_metadata/peilbuizen_metadata.xlsx"
path_bemonstering = basedir / "05_waterkwaliteitmonsters/bemonstering_10-08-2022.xlsx"


metadata = pd.read_excel(path_metadata).set_index("Peilbuis")
df = pd.read_excel(path_bemonstering).set_index("Peilbuis")

depth_nap = metadata["Top_PB (m NAP)"] - metadata["Diepte_PB (m-top_pb)"]

df = df.iloc[1:]
df = df.replace("n.a.", np.nan)
df.columns = df.columns.str.replace("\n \n", "")
df.columns = df.columns.str.replace("\n", "")
df = df.join(depth_nap.to_frame("Diepte filter (m NAP)"))

# # Assuming 'correlation_matrix' is your correlation matrix dataframe
fig, ax = plt.subplots(1, 1, figsize=(15, 15), dpi=400, sharex=True)
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=False, cmap="RdYlGn", ax=ax)
plt.title("Correlation Matrix")
plt.show()

# %% convert to meq/l
df["Chloride_meq"] = df["Chloride"] * 1 / element("Cl").atomic_weight  # mEq/l
df["Sodium_meq"] = df["Sodium"] * 1 / element("Na").atomic_weight
df["Calcium_meq"] = df["Calcium"] * 2 / element("Ca").atomic_weight
df["HCO3-_meq"] = df["HCO3-"] / 61.0168
df["Bromide_meq"] = df["Bromide"] / element("Br").atomic_weight
df["Sulfate_meq"] = df["Sulfate"] * 2 / 96.06
df["Magnesium_meq"] = df["Magnesium"] * 2 / element("Mg").atomic_weight  # mEq/l
df["Potassium_meq"] = df["Potassium"] / 1000 * 1 / element("K").atomic_weight

df["BEX"] = (
    df["Magnesium_meq"] + df["Sodium_meq"] + df["Potassium_meq"]
) - 1.0716 * df["Chloride_meq"]

# %% CHLORIDE VS NATRIUM
fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
ax.plot([0, 500], [0, 500], "lightgrey", lw=2)
df.plot.scatter(ax=ax, x="Sodium_meq", y="Chloride_meq", color="black")
ax.set_xlabel("Natrium (mEq/L)")
ax.set_ylabel("Chloride (mEq/L)")
ax.set_ylim([0, 500])
ax.set_xlim([0, 500])

# for k, v in df.iterrows():
#     ax.text(v['Sodium_meq']+5, v['Chloride_meq'], k,fontsize = 8, ha = 'left', va='center')
ax.text(480, 480, "1:1", fontsize=8, color="grey", rotation=45, ha="center", va="top")

# %% calcium vs bicarbonate
fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
ax.plot([0, 25], [0, 50], "lightgrey", lw=2)
df.plot.scatter(ax=ax, x="Calcium_meq", y="HCO3-_meq", color="black")
ax.set_xlabel("Calcium (mEq/L)")
ax.set_ylabel("Bicarbonaat (mEq/L)")
ax.set_ylim([0, 30])
ax.set_xlim([0, 30])
# for k, v in df.iterrows():
#     ax.text(v['Calcium_meq']+0.2, v['HCO3-_meq'], k,fontsize = 8, ha = 'left', va='center')
ax.text(13, 27, "1:2", fontsize=8, color="grey", rotation=60, ha="center", va="top")


# %% calcium vs natrium

fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)

df.plot.scatter(ax=ax, x="Sodium_meq", y="Calcium_meq", color="black")
ax.set_ylabel("Calcium (mEq/L)")
ax.set_xlabel("Natrium (mEq/L)")
ax.set_ylim([0, 30])
ax.set_xlim([0, 370])
# for k, v in df.iterrows():
#     ax.text(v['Sodium_meq']+3, v['Calcium_meq'], k,fontsize = 8, ha = 'left', va='center')

# %% ijzer vs sulfaat
fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)

df.plot.scatter(ax=ax, x="Fe", y="Sulfate_meq", color="black")
ax.set_xlabel("Fe (ppm)")
ax.set_ylabel("Sulfate (mEq/L)")
ax.set_ylim([0, 30])
ax.set_xlim([0, 15])
for k, v in df.iterrows():
    ax.text(v["Fe"] + 0.1, v["Sulfate_meq"], k, fontsize=8, ha="left", va="center")


# %% chloride vs bromide

fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
df.plot.scatter(ax=ax, x="Chloride_meq", y="Bromide_meq", color="black")
ax.set_xlabel("Chloride (mEq/L)")
ax.set_ylabel("Bromide (mEq/L)")
ax.set_ylim([0, 0.7])
ax.set_xlim([0, 400])

for k, v in df.iterrows():
    ax.text(
        v["Chloride_meq"] + 3, v["Bromide_meq"], k, fontsize=8, ha="left", va="center"
    )

    # %https://www.google.com/search?q=redox+keten+in+ondergrond&tbm=isch&hl=en-US&sa=X&ved=2ahUKEwiTxtbc--z-AhURhP0HHTErCO4QBXoECAEQIQ&biw=1903&bih=956#imgrc=VdzCdg1H9cduKM
# %% Sr vs chloride
fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
df.plot.scatter(ax=ax, x="Chloride_meq", y="Sr 88", color="black")
ax.set_xlabel("Chloride (mEq/L)")
ax.set_ylabel("Sr 88 (ppb)")
ax.set_ylim([0, 6200])
ax.set_xlim([0, 400])

for k, v in df.iterrows():
    ax.text(v["Chloride_meq"] + 3, v["Sr 88"], k, fontsize=8, ha="left", va="center")

# %% depth
fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
ax.fill_between([0, 400], -17, -19, color="green", alpha=0.4)
ax.text(200, -18, "-17 m NAP kleilaag", fontsize=8, ha="left", va="center")
ax.fill_between([0, 400], -40, -42, color="green", alpha=0.4)
ax.text(200, -41, "Eemklei", fontsize=8, ha="left", va="center")
df.plot.scatter(ax=ax, x="Chloride_meq", y="Diepte filter (m NAP)", color="black")
ax.set_xlabel("Chloride (mEq/L)")
ax.set_xlim([0, 400])
ax.set_ylim([-65, 0])
for k, v in df.iterrows():
    ax.text(
        v["Chloride_meq"] + 3,
        v["Diepte filter (m NAP)"],
        k,
        fontsize=8,
        ha="left",
        va="center",
    )

fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
ax.fill_between([0, 10], -17, -19, color="green", alpha=0.4)
ax.text(5, -18, "-17 m NAP kleilaag", fontsize=8, ha="left", va="center")
ax.fill_between([0, 10], -40, -42, color="green", alpha=0.4)
ax.text(5, -41, "Eemklei", fontsize=8, ha="left", va="center")
df.plot.scatter(ax=ax, x="Fe", y="Diepte filter (m NAP)", color="black")
ax.set_xlabel("Fe (ppm)")
ax.set_xlim([0, 10])
ax.set_ylim([-65, 0])
for k, v in df.iterrows():
    ax.text(
        v["Fe"] + 0.1, v["Diepte filter (m NAP)"], k, fontsize=8, ha="left", va="center"
    )

fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
ax.fill_between([0, 15], -17, -19, color="green", alpha=0.4)
ax.text(5, -18, "-17 m NAP kleilaag", fontsize=8, ha="left", va="center")
ax.fill_between([0, 15], -40, -42, color="green", alpha=0.4)
ax.text(5, -41, "Eemklei", fontsize=8, ha="left", va="center")
df.plot.scatter(ax=ax, x="Sulfate_meq", y="Diepte filter (m NAP)", color="black")
ax.set_xlabel("Sulfate (mEq/L)")
ax.set_xlim([0, 15])
ax.set_ylim([-65, 0])
for k, v in df.iterrows():
    ax.text(
        v["Sulfate_meq"] + 0.1,
        v["Diepte filter (m NAP)"],
        k,
        fontsize=8,
        ha="left",
        va="center",
    )

fig, ax = plt.subplots(1, 1, figsize=(7.5, 7.5), dpi=400, sharex=True)
ax.fill_between([-50, 10], -17, -19, color="green", alpha=0.4)
ax.text(-1, 0, "$verzilting$", fontsize=8, ha="right", va="top", color="blue")
ax.text(1, 0, "$verzoeting$", fontsize=8, ha="left", va="top", color="blue")
ax.vlines(x=0, ymin=-65, ymax=0, lw=0.5, ls="--", color="black")
ax.text(-49, -18, "-17 m NAP kleilaag", fontsize=8, ha="left", va="center")
ax.fill_between([-50, 10], -40, -42, color="green", alpha=0.4)
ax.text(-49, -41, "Eemklei", fontsize=8, ha="left", va="center")
df.plot.scatter(ax=ax, x="BEX", y="Diepte filter (m NAP)", color="black")
ax.set_xlabel("BEX")
ax.set_ylim([-65, 0])
ax.set_xlim([-50, 10])
for k, v in df.iterrows():
    ax.text(
        v["BEX"] + 0.5,
        v["Diepte filter (m NAP)"],
        k,
        fontsize=8,
        ha="left",
        va="center",
    )
plt.tight_layout()
fig.savefig(basedir.joinpath(f"06_webviewer/maps_figures/figure_bex-index.png"))
