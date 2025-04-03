from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def open_borelog(path, correct_depth: float = 0.0):
    df = pd.read_csv(path, skiprows=25, sep="\s+")
    df = df.iloc[1:]

    df["Depth"] = pd.to_numeric(df["Depth"]) + correct_depth
    df["IL.CNT"] = pd.to_numeric(df["IL.CNT"])

    return df


projectdir = Path(
    r"n:\Projects\11207500\11207510\B. Measurements and calculations\04_boorgatmetingen\data_03122024"
)

path_a_2024 = projectdir / "20241203_Ijmuiden_A", "A_CNT_1186slim1_2.asc"
path_b_2024 = projectdir / "20241203_Ijmuiden_B", "B_CNT_1186slim1_2.asc"
path_bl02_2024 = projectdir / "20241203_Ijmuiden_BL-02", "BL-02_CNT_1186slim1_2.asc"
path_e_2024 = projectdir / "20241203_Ijmuiden_E_2", "E_2_CNT_1186slim1_2.asc"
path_d_2024 = projectdir / "20241203_Ijmuiden_D", "D_CNT_1186slim1_2.asc"
path_c_2024 = projectdir / "20241203_Ijmuiden_C", "C_CNT_1186slim1_2.asc"

borelog_a = open_borelog(path_a_2024, correct_depth=-0.39)
borelog_a.to_csv(
    projectdir / "20241203_Ijmuiden_A/corrected_20241203_A_CNT_1186slim1_2.csv",
    index=False,
    sep=";",
)

borelog_b = open_borelog(path_b_2024, correct_depth=-0.49)
borelog_b.to_csv(
    projectdir / "20241203_Ijmuiden_B/corrected_20241203_B_CNT_1186slim1_2.csv",
    index=False,
    sep=";",
)

borelog_bl02 = open_borelog(path_bl02_2024, correct_depth=-0.37)
borelog_bl02.to_csv(
    projectdir / "20241203_Ijmuiden_BL-02/corrected_20241203_BL-02_CNT_1186slim1_2.csv",
    index=False,
    sep=";",
)

borelog_e = open_borelog(path_e_2024, correct_depth=-0.23)
borelog_e.to_csv(
    projectdir / "20241203_Ijmuiden_E_2/corrected_20241203_E_2_CNT_1186slim1_2.csv",
    index=False,
    sep=";",
)

borelog_d = open_borelog(path_d_2024, correct_depth=-0.40)
borelog_d.to_csv(
    projectdir / "20241203_Ijmuiden_D/corrected_20241203_D_CNT_1186slim1_2.csv",
    index=False,
    sep=";",
)

borelog_c = open_borelog(path_c_2024, correct_depth=-0.20)
borelog_c.to_csv(
    projectdir / "20241203_Ijmuiden_C/corrected_20241203_C_CNT_1186slim1_2.csv",
    index=False,
    sep=";",
)
