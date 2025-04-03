import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

projectdir = Path(
    r"n:\Projects\11207500\11207510\B. Measurements and calculations\04_boorgatmetingen"
)

dir_2024 = projectdir.joinpath("data_03122024")

# meetpunt E
path_A_2024 = dir_2024.joinpath("20241203_Ijmuiden_A", "A_CNT_1186slim1_2.asc")
path_B_2024 = dir_2024.joinpath("20241203_Ijmuiden_B", "B_CNT_1186slim1_2.asc")
path_BL02_2024 = dir_2024.joinpath(
    "20241203_Ijmuiden_BL-02", "BL-02_CNT_1186slim1_2.asc"
)
path_E_2024 = dir_2024.joinpath("20241203_Ijmuiden_E_2", "E_2_CNT_1186slim1_2.asc")
path_D_2024 = dir_2024.joinpath("20241203_Ijmuiden_D", "D_CNT_1186slim1_2.asc")
path_C_2024 = dir_2024.joinpath("20241203_Ijmuiden_C", "C_CNT_1186slim1_2.asc")


def open_log(path, correct_depth: float = 0.0):
    df = pd.read_csv(path, skiprows=25, sep="\s+")
    df = df.iloc[1:]

    df["Depth"] = pd.to_numeric(df["Depth"]) + correct_depth
    df["IL.CNT"] = pd.to_numeric(df["IL.CNT"])

    return df


borelog_a = open_log(path_A_2024, correct_depth=-0.39)
borelog_a.to_csv(
    dir_2024.joinpath(
        "20241203_Ijmuiden_A", "corrected_20241203_A_CNT_1186slim1_2.csv"
    ),
    index=False,
    sep=";",
)

borelog_b = open_log(path_B_2024, correct_depth=-0.49)
borelog_b.to_csv(
    dir_2024.joinpath(
        "20241203_Ijmuiden_B", "corrected_20241203_B_CNT_1186slim1_2.csv"
    ),
    index=False,
    sep=";",
)

borelog_bl02 = open_log(path_BL02_2024, correct_depth=-0.37)
borelog_bl02.to_csv(
    dir_2024.joinpath(
        "20241203_Ijmuiden_BL-02", "corrected_20241203_BL-02_CNT_1186slim1_2.csv"
    ),
    index=False,
    sep=";",
)

borelog_E = open_log(path_E_2024, correct_depth=-0.23)
borelog_E.to_csv(
    dir_2024.joinpath(
        "20241203_Ijmuiden_E_2", "corrected_20241203_E_2_CNT_1186slim1_2.csv"
    ),
    index=False,
    sep=";",
)

borelog_D = open_log(path_D_2024, correct_depth=-0.40)
borelog_D.to_csv(
    dir_2024.joinpath(
        "20241203_Ijmuiden_D", "corrected_20241203_D_CNT_1186slim1_2.csv"
    ),
    index=False,
    sep=";",
)

borelog_C = open_log(path_C_2024, correct_depth=-0.20)
borelog_C.to_csv(
    dir_2024.joinpath(
        "20241203_Ijmuiden_C", "corrected_20241203_C_CNT_1186slim1_2.csv"
    ),
    index=False,
    sep=";",
)
