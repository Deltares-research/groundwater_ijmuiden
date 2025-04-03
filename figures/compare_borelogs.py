import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def open_log(path, surface_level: float, correct_depth: float = 0.0):
    df = pd.read_csv(path, skiprows=25, sep="\s+")
    df = df.iloc[1:]

    df["Depth"] = pd.to_numeric(df["Depth"]) + correct_depth
    df["Depth (m-nap)"] = surface_level - df["Depth"]
    df["IL.CNT"] = pd.to_numeric(df["IL.CNT"])
    df = df.set_index("Depth (m-nap)")
    df = df[df["IL.CNT"] > -900]
    return df

projectdir = Path(
    r"n:\Projects\11207500\11207510\B. Measurements and calculations\04_boorgatmetingen"
)

dir_2022 = projectdir / "data_08082022"
dir_2023 = projectdir / "data_25052023"
dir_2024 = projectdir / "data_03122024"

# meetpunt E
path_E_2022 = dir_2022 / "20220808_E_2", "E_2_CNT_1186slim1_2.asc"
path_E_2023 = dir_2023 / "20230525_E_2", "E_2_CNT_1186slim1_2.asc"
path_E_2024 = dir_2024 / "20241203_Ijmuiden_E_2", "E_2_CNT_1186slim1_2.asc"

# meetpunt C
path_C_2022 = dir_2022 / "20220808_C_3", "20220808_C_3_CNT_1186slim1_2.asc"
path_C_2023 = dir_2023 / "20230525_C_3", "C_3_CNT_1186slim1_2.asc"
path_C_2024 = dir_2024 / "20241203_Ijmuiden_C", "C_CNT_1186slim1_2.asc"

# meetpunt D
path_D_2023 = dir_2023 / "20230525_D_2", "D_2_CNT_1186slim1_2.asc"
path_D_2024 = dir_2024 / "20241203_Ijmuiden_D", "D_CNT_1186slim1_2.asc"




fig, ax = plt.subplots(dpi=400, ncols=3, sharex=True, sharey=True)

df_D_2023 = open_log(path_D_2023, surface_level=0.98)
df_D_2024 = open_log(path_D_2024, surface_level=0.98, correct_depth=-0.40)
ax[0].plot(df_D_2023["IL.CNT"], df_D_2023.index, label="2023", color="green", lw=1.0)
ax[0].plot(df_D_2024["IL.CNT"], df_D_2024.index, label="2024", color="red", lw=1.0)
ax[0].set_xlim(0, 750)

df_C_2022 = open_log(path_C_2022, surface_level=5.0)
df_C_2023 = open_log(path_C_2023, surface_level=5.0)
df_C_2024 = open_log(path_C_2024, surface_level=5.0, correct_depth=-0.20)
ax[1].plot(df_C_2022["IL.CNT"], df_C_2022.index, label="2022", color="darkblue", lw=1.0)
ax[1].plot(df_C_2023["IL.CNT"], df_C_2023.index, label="2023", color="green", lw=1.0)
ax[1].plot(df_C_2024["IL.CNT"], df_C_2024.index, label="2024", color="red", lw=1.0)

df_E_2022 = open_log(path_E_2022, surface_level=3.18)
df_E_2023 = open_log(path_E_2023, surface_level=3.18)
df_E_2024 = open_log(path_E_2024, surface_level=3.18)
ax[2].plot(df_E_2022["IL.CNT"], df_E_2022.index, label="2022", color="darkblue", lw=1.0)
ax[2].plot(df_E_2023["IL.CNT"], df_E_2023.index, label="2023", color="green", lw=1.0)
ax[2].plot(df_E_2024["IL.CNT"], df_E_2024.index, label="2024", color="red", lw=1.0)
ax[2].legend(frameon=False)

ax[0].set_ylabel("Diepte (m NAP)")
ax[0].set_xlabel("EM-inductie (mS/m)")
ax[1].set_xlabel("EM-inductie (mS/m)")
ax[2].set_xlabel("EM-inductie (mS/m)")
ax[0].grid(color="lightgrey")
ax[1].grid(color="lightgrey")
ax[2].grid(color="lightgrey")

ax[0].set_title("D")
ax[1].set_title("C")
ax[2].set_title("E")

ax[0].fill_between(
    x=[0, 750], y1=-18, y2=-16, color="#04724D", alpha=0.4, edgecolor="none"
)
ax[2].text(x=750, y=-17, s="Klei/veenlaag", ha="right", va="center", fontsize=8)
ax[0].fill_between(x=[0, 750], y1=-40, y2=-38, color="#04724D", alpha=0.4)
ax[2].text(x=750, y=-39, s="Eemklei", ha="right", va="center", fontsize=8)

ax[1].fill_between(
    x=[0, 750], y1=-18, y2=-16, color="#04724D", alpha=0.4, edgecolor="none"
)
ax[1].fill_between(x=[0, 750], y1=-40, y2=-38, color="#04724D", alpha=0.4)

ax[2].fill_between(
    x=[0, 750], y1=-18, y2=-16, color="#04724D", alpha=0.4, edgecolor="none"
)
ax[2].fill_between(x=[0, 750], y1=-40, y2=-38, color="#04724D", alpha=0.4)
