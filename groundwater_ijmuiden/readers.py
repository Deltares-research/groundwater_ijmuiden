import pandas as pd

import chardet
import numpy as np
from pathlib import Path


def read_diver(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        usecols=[0, 1, 2],
        names=["date", "diver_pressure (cmH2O)", "temperature (degC)"],
        decimal=",",
        skiprows=52,
        delimiter=";",
        encoding="ISO-8859-1",
        engine="python",
    )
    df = df[:-1].replace("     ", np.nan)
    df["diver_pressure (mH2O)"] = pd.to_numeric(df["diver_pressure (cmH2O)"]) / 100
    df = df.drop(columns=["diver_pressure (cmH2O)"])
    df["temperature (degC)"] = pd.to_numeric(df["temperature (degC)"])
    df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d %H:%M:%S")
    df = df.set_index("date")
    return df


def read_barometer(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        usecols=[0, 1],
        names=["date", "air_pressure (cmH2O)"],
        decimal=",",
        skiprows=52,
        delimiter=";",
        encoding="ISO-8859-1",
        engine="python",
    )
    df = df[:-1].replace("     ", np.nan)
    df["air_pressure (mH2O)"] = pd.to_numeric(df["air_pressure (cmH2O)"]) / 100
    df = df.drop(columns=["air_pressure (cmH2O)"])
    df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d %H:%M:%S")
    df = df.set_index("date")
    return df


def read_ec_measurement(path: str | Path) -> pd.Series:
    """
    Open csv-file with ec-measurements from field campaig and convert to mS/cm
    """
    df = pd.read_csv(
        path,
        decimal=",",
        skiprows=19,
        delimiter=";",
        encoding="ISO-8859-1",
        engine="python",
        index_col="Sample number",
    )

    df["Electrical Conductivity[mS/cm]"] = df["Electrical Conductivity[ÂµS/cm]"] / 1000

    return df["Electrical Conductivity[mS/cm]"]


def read_gw_measurements(path: str | Path):
    """
    Open csv-file (export by diver office) with groundwater manual measurement from field campaign.
    """
    with open(
        path,
        "rb",
    ) as f:
        enc = chardet.detect(f.read())

    df = pd.read_csv(
        path,
        skiprows=1,
        delimiter=";",
        encoding=enc["encoding"],
        names=["Peilbuis", "datetime", "head (m-ztop)"],
    )

    df["datetime"] = pd.to_datetime(df["datetime"], format="%d-%m-%Y %H:%M:%S")
    df["head (m-ztop)"] = pd.to_numeric(df["head (m-ztop)"]) / 100

    return df.set_index("Peilbuis")
