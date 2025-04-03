# %%
import functools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress

metadata = pd.read_excel(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/01_metadata/peilbuizen_metadata.xlsx"
)
handmetingen = pd.read_csv(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/02_handmetingen/handmetingen_09082022.csv",
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

# %% groundwater
df = metadata[["Peilbuis"]].copy().set_index("Peilbuis")
for name, row in df.iterrows():

    if name in [
        "B25A0942_3",
        "B25A0942_5",
        "B25A0942_6",
        "B25A0942_7",
        "D_2",
        "B25A0942_3_extra",
        "B25A0942_5_extra",
        "B25A0942_6_extra",
        "B25A0942_7_extra",
        "Z13PB600_1_extra",
    ]:
        continue
    else:
        df.loc[name, "EC [mS/cm]"] = (
            handmetingen.loc[name, "Electrical Conductivity[ÂµS/cm]"] / 1000
        )
        df.loc[name, "Cl [mg/l]"] = bemonstering.loc[name, "Chloride"]

df = df.dropna(axis=0)
df = df.sort_values("EC [mS/cm]")

lower_ec = df["EC [mS/cm]"] <= 2.0
slope_1, intercept_1, r_1, p_1, se_1 = linregress(
    x=df.loc[lower_ec, "EC [mS/cm]"], y=df.loc[lower_ec, "Cl [mg/l]"]
)


def model(x, slope, x1, y1):
    return slope * (x - x1) + y1


x1 = 2  # ec
y1 = slope_1 * 2 + intercept_1  # cl
partial_model = functools.partial(model, x1=x1, y1=y1)
slope_2, __ = curve_fit(
    partial_model, df.loc[~lower_ec, "EC [mS/cm]"], df.loc[~lower_ec, "Cl [mg/l]"]
)
intercept_2 = model(0, slope_2, x1, y1)

# slope_2, intercept_2, r_2, p_2, se_2 = linregress(x = df.loc[~lower_ec,'EC [mS/cm]'], y = df.loc[~lower_ec,'Cl [mg/l]'])


# %% literature


# EC < 2 mS/cm
def lowECtoCl(ec):
    # units mS/cm --> mg/l
    slope_1 = 235.97
    intercept_1 = -146.21
    return slope_1 * ec + intercept_1


def highECtoCl(ec):
    # units mS/cm --> mg/l
    slope_2 = 374.43
    intercept_2 = -423.12
    return slope_2 * ec + intercept_2


def ECtoCl(ec):
    lowECs = ec <= 2
    cl = np.full_like(ec, np.nan)
    cl[lowECs] = lowECtoCl(ec[lowECs])
    cl[~lowECs] = highECtoCl(ec[~lowECs])
    return cl


# %%
fig, ax = plt.subplots(
    nrows=1, ncols=1, dpi=400, figsize=(8.27, 11.69 / 3), sharey=True, sharex=True
)
df.plot.scatter("EC [mS/cm]", "Cl [mg/l]", ax=ax, color="red")
ax.plot(
    np.arange(0, 40, 0.1),
    ECtoCl(np.arange(0, 40, 0.1)),
    color="blue",
    linewidth=2,
    ls="--",
)
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
ax.annotate(text="brak-zout", xy=(35, 2150))
ax.annotate(text="zout", xy=(35, 12000))
ax.set_xlim([0, 40])
ax.set_ylim([0, 20000])
ax.set_title("Relatie EC en Chloride-concentratie", fontweight="bold", size=10)
