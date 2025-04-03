# %%
from pathlib import Path

import pandas as pd

import groundwater_ijmuiden as gij
from runfiles.rename import rename_well

project_dir = Path(r"N:/Projects/11207500/11207510/B. Measurements and calculations")
measurements_dir = project_dir / "02_handmetingen"
diver_dir = project_dir / "03_divers"
output_dir = diver_dir / "zoetwaterstijghoogte"

path_metadata = project_dir / "01_metadata", "peilbuizen_metadata.xlsx"
path_baro = diver_dir / "diverdata/KNMI 240 Schiphol.csv"
path_gw_measurements = diver_dir / "Manual Measurements-IJmuiden.csv"

metadata = pd.read_excel(path_metadata, index_col=0)
# % open ec field measurements
campaign_dates = [
    "09082022",
    "07022023",
    "23052023",
    "19092023",
    "23012024",
    "10042024",
    "22052024",
    "02122024",
]
ec_measurements = pd.DataFrame()
for date in campaign_dates:
    path = measurements_dir / f"handmetingen_{date}.csv"

    df = gij.read_ec_measurement(path)
    date = pd.to_datetime(date, format="%d%m%Y")

    ec_measurements[date] = df

# % open groundwater hand measurements
gw_measurements = gij.read_gw_measurements(path_gw_measurements)
gw_measurements.index = [rename_well(name) for name in gw_measurements.index.tolist()]
project_baro = gij.read_barometer(path_baro)

# %%
start_date = "20-05-2022"
end_date = "05-12-2024"
386
well_ids = metadata.index.to_list()
well_ids = ["BL-01_2"]
for well_id in well_ids:
    print(well_id)

    metadata_well = metadata.loc[well_id]

    if not isinstance(metadata_well.DiverID, str):
        continue

    aquifer = "aquifer_" + well_id.split("_")[-1]
    if aquifer == "aquifer_1":
        reference_level = -15
    elif aquifer == "aquifer_2":
        reference_level = -25
    elif aquifer == "aquifer_3":
        reference_level = -50
    else:
        continue

    path_diver = diver_dir.joinpath("diverdata", f"{well_id}.csv")
    diver = gij.read_diver(path_diver)

    monitoring_well = gij.MonitoringWell(
        well_id=well_id,
        reference_level=reference_level,
        ztop=metadata_well["Top_PB (m NAP)"],
        well_depth=metadata_well["Diepte_PB (m-top_pb)"],
        cable_length=metadata_well["kabellengte (m)"],
        start_date=start_date,
        end_date=end_date,
    )

    monitoring_well.add_barometer(project_baro)

    if well_id in ["BL-01_1"]:
        monitoring_well.add_diverdata(diver, zscore_limit=7)
    else:
        monitoring_well.add_diverdata(diver)

    # update well properties (some wells were shortened or/and extend several times)
    for i in [1, 2, 3]:  # Adjust the range as needed
        date_key = f"datum_aanpassing_{i}"
        cable_length_key = f"kabellengte_{i} (m)"
        top_pb_key = f"Top_PB_{i} (m NAP)"

        if not pd.isna(metadata_well[date_key]):
            if not pd.isna(metadata_well[cable_length_key]):
                monitoring_well.update_properties(
                    new_cable_length=metadata_well[cable_length_key],
                    date_correction=metadata_well[date_key],
                )
            if not pd.isna(metadata_well[top_pb_key]):
                monitoring_well.update_properties(
                    new_ztop=metadata_well[top_pb_key],
                    date_correction=metadata_well[date_key],
                )

    # add ec measurements to calculate water density
    ec_measurements_well = ec_measurements.loc[well_id]
    monitoring_well.add_ec_measurements(
        ec_measurements_well.to_frame("electrical_conductivity (mS/cm)")
    )

    # add gw measuremets for water level corrections
    gw_measurements_well = gw_measurements.loc[well_id].set_index("datetime")
    monitoring_well.add_gw_measurements(gw_measurements_well)

    # calculate water level.
    if well_id in [
        "Z13PB600_1",
        "B25A0942_3",
        "RWS-B27_1",
        "C_1",
        "C_2",
        "C_3",
        "BK-8.25_2",
        "BL-01_1",
    ]:
        monitoring_well.barometric_compensation(
            match_gw_measurements=True,
            method="penultimate",
        )

    elif well_id in ["D_1", "B25A0942_1"]:
        monitoring_well.barometric_compensation(
            match_gw_measurements=True, method="penultimate"
        )
    else:
        monitoring_well.barometric_compensation(match_gw_measurements=False)

    if well_id == "C_2":
        monitoring_well.drop_data(before="11-08-2022")

    if well_id == "C_3":
        monitoring_well.drop_data(before="10-10-2022")

    if well_id == "Z13PB600_1":
        monitoring_well.drop_data(between=["18-09-2023", "6-10-2023"])

    if well_id == "RWS-04-2_2":
        monitoring_well.drop_data(between=["27-07-2022", "13-9-2022"])

    if well_id == "RWS-04-3_1":
        monitoring_well.drop_data(before="13-9-2022")

    fig = gij.plot_groundwater(monitoring_well, freq="h")
    fig.savefig(
        rf"n:\Projects\11207500\11207510\C. Report - advise\figuren\tijdreeksen_december_2024\{well_id}.png"
    )

    monitoring_well.export_fresh_water_head(output_dir.joinpath(f"{well_id}.csv"))

# %%
